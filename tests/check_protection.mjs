import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {execFileSync} from 'node:child_process';

const temporary = mkdtempSync(join(tmpdir(), 'site-protection-'));
try {
  const project = join(temporary, 'company');
  const build = JSON.parse(execFileSync('python3', ['scripts/orchestrator.py', '--name', 'Security Fixture',
    '--intro', 'Synthetic test only', '--industry', 'machinery', '--out', project], {encoding:'utf8'}));
  const deploy = build.deployment_directory;
  const config = JSON.parse(readFileSync(join(deploy, 'wrangler.json')));
  const policy = JSON.parse(readFileSync(join(deploy, 'policy.json')));
  const source = readFileSync(join(deploy, 'worker.mjs'), 'utf8');
  assert.equal(resolve(deploy, config.assets.directory), build.site_directory);
  assert.equal(config.assets.run_worker_first, true);
  assert.equal(build.protection_runtime, 'NOT_RUN');
  assert.ok(!policy.paths.some(p => /private|policy.json|worker.mjs/.test(p)));
  assert.ok(policy.paths.includes('/robots.txt') && policy.paths.includes('/products/'));
  const load = async p => (await import('data:text/javascript;base64,' + Buffer.from(
    source.replace("import policy from './policy.json';", `const policy = ${JSON.stringify(p)};`)).toString('base64'))).default;
  let worker = await load(policy);
  let readSuccess = true, writeSuccess = true, assetCalls = 0, readCalls = 0, writeCalls = 0, upstreamCalls = 0;
  const env = {
    ASSETS:{fetch:async () => {assetCalls++; return new Response('same public HTML', {headers:{'Content-Type':'text/html'}});}},
    READ_LIMITER:{limit:async ({key}) => {readCalls++; assert.equal(key, policy.siteId + ':192.0.2.1'); return {success:readSuccess};}},
    INQUIRY_LIMITER:{limit:async () => {writeCalls++; return {success:writeSuccess};}},
  };
  const request = (path='/', options={}, cf) => {
    const r = new Request('https://example.com' + path, {...options,
      headers:{'CF-Connecting-IP':'192.0.2.1', ...options.headers}});
    if (cf) Object.defineProperty(r,'cf',{value:cf});
    return r;
  };
  for (const ua of ['Browser', 'Googlebot', 'OAI-SearchBot', 'Bingbot', 'PerplexityBot', 'UnknownCrawler']) {
    const r = await worker.fetch(request('/', {headers:{'User-Agent':ua}}),env);
    assert.equal(r.status,200); assert.equal(await r.text(),'same public HTML');
    assert.equal(r.headers.get('X-Frame-Options'),'DENY');
    assert.ok(r.headers.get('Content-Security-Policy').includes("frame-ancestors 'none'"));
    assert.equal(r.headers.get('X-Robots-Tag'),null);
  }
  for (const path of ['/private/raw/logo.png','/.env','/.git/config','/policy.json','/%70rivate/raw','/missing']) {
    const before = assetCalls;
    assert.equal((await worker.fetch(request(path),env)).status,404);
    assert.equal(assetCalls,before);
  }
  assert.equal((await worker.fetch(request('/',{method:'DELETE'}),env)).status,405);
  assert.equal(await (await worker.fetch(request('/',{method:'HEAD'}),env)).text(),'');
  for (const path of ['/robots.txt','/sitemap.xml','/css/site.css','/products/']) {
    assert.equal((await worker.fetch(request(path),env)).status,200);
  }
  readSuccess = false;
  for (const headers of [{'User-Agent':'Googlebot'}, {'X-Verified-Bot':'true'}, {'cf-client-bot':'true'}]) {
    const r = await worker.fetch(request('/?rotate=anything',{headers}),env);
    assert.equal(r.status,429); assert.equal(r.headers.get('Retry-After'),'60');
    assert.equal(r.headers.get('Cache-Control'),'no-store');
  }
  const before = readCalls;
  assert.equal((await worker.fetch(request('/',{}, {botManagement:{verifiedBot:true}}),env)).status,200);
  assert.equal(readCalls,before);
  assert.equal((await worker.fetch(request('/',{}, {botManagement:{verifiedBot:'true'}}),env)).status,429);
  readSuccess = true;
  assert.equal((await worker.fetch(request(),env)).status,200);
  const degraded = await worker.fetch(request(),{ASSETS:env.ASSETS});
  assert.equal(degraded.status,200); assert.equal(degraded.headers.get('X-Site-Protection'),'degraded');

  worker = await load({...policy,inquiryPath:'/api/inquiry'});
  const post = (body='{}', extra={}, cf) => request('/api/inquiry', {method:'POST',body,
    headers:{'Origin':'https://example.com','Content-Type':'application/json',...extra}}, cf);
  assert.equal((await worker.fetch(request('/api/inquiry'),env)).status,405);
  assert.equal((await worker.fetch(post('{}',{Origin:'https://evil.example'}),env)).status,403);
  assert.equal((await worker.fetch(post(),env)).status,503);
  env.INQUIRY = {fetch:async r => {upstreamCalls++; assert.equal(await r.text(),'{}');
    return new Response('{"accepted":true,"reference":"test-only"}', {headers:{'Content-Type':'application/json'}});}};
  assert.equal((await worker.fetch(post('x'.repeat(16385)),env)).status,413);
  assert.equal(upstreamCalls,0);
  let r = await worker.fetch(post(),env);
  assert.equal(r.status,200); assert.equal(r.headers.get('Cache-Control'),'no-store');
  assert.equal((await r.json()).reference,'test-only');
  writeSuccess = false;
  r = await worker.fetch(post('{}',{}, {botManagement:{verifiedBot:true}}),env);
  assert.equal(r.status,429); assert.equal(upstreamCalls,1);
  assert.equal((await worker.fetch(post(),{ASSETS:env.ASSETS,INQUIRY:env.INQUIRY})).status,503);
  assert.ok(writeCalls > 0);
  console.log('PASS: generated protection bundle, crawl parity, path isolation, rate limits, forgery, failure modes and inquiry boundary');
} finally { rmSync(temporary,{recursive:true,force:true}); }
