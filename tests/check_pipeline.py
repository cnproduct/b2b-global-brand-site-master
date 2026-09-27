#!/usr/bin/env python3
"""Offline regression: actual generated artifacts, trust boundaries and failure signals."""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import sitekit
from site_compiler import build,starter,origin
from validate_site import audit_site
from extract_brand_dna import self_test as brand_test


def rejected(function):
    try: function()
    except (ValueError,FileExistsError): return
    raise AssertionError('expected rejection')


def run():
    sitekit.self_test();brand_test()
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary);intro=root/'intro.txt';intro.write_text('INTERNAL_CANARY: no claims approved. <script>alert(1)</script>',encoding='utf-8')
        for profile in sitekit.profiles():
            p=sitekit.project_init('Example <Brand> & Co.',profile['id'],intro,None,root/profile['id'])
            sitekit.write(p/'content/site.json',starter(p))
            site=build(p)
            report=audit_site(site)
            assert report['status']=='PASS',report
            assert len(list(site.rglob('*.html')))==6
            assert len(sitekit.read(p/'private/module-coverage.json'))==21
            assert not any('INTERNAL_CANARY' in f.read_text() for f in site.rglob('*') if f.is_file())
            assert not (site/'private').exists()
            rejected(lambda: build(p,True))
        p=root/'machinery'
        cards=sitekit.read(p/'private/knowledge-cards.json');card=cards[0]
        card.update(title='Test specimen width',conclusion='40 mm <script>not executable</script>',conditions='Synthetic fixture only',status='verified_fact',sensitivity='public',public_claim_approved=True)
        sitekit.write(p/'private/knowledge-cards.json',cards)
        meta=sitekit.read(p/'project.json');meta.update(domain='https://example.com',contact='test@example.com',identity_approved=True,contact_approved=True)
        sitekit.write(p/'project.json',meta)
        config=sitekit.read(p/'content/site.json')
        for page in config['pages']:
            page['reviewed_for_public']=True
            page['sections']=[{'kind':'editorial','heading':page['heading'],'text':'Synthetic '+page['title']+' page.','reviewed_for_public':True}]
        config['pages'][0]['sections'].append({'kind':'specifications','heading':'Specification','claim_ids':[card['kb_id']]})
        config['pages'][1]['estimator']=True
        config['llms']=True;config['training_bot_policy']='disallow'
        sitekit.write(p/'content/site.json',config)
        site=build(p,True);report=audit_site(site,True,'https://example.com')
        assert report['status']=='PASS',report
        html=(site/'index.html').read_text()
        assert '<script>not executable</script>' not in html and '&lt;script&gt;' in html
        assert 'noindex' not in html
        assert 'GPTBot\nDisallow: /' in (site/'robots.txt').read_text()
        assert 'source_refs' not in ''.join(f.read_text() for f in site.rglob('*') if f.is_file())
        assert (site/'css/tokens.css').is_file() and (site/'js/sourcing_estimator.js').is_file()
        assert (site/'llms.txt').is_file()
        # Fact revocation applies equally to editorial references and asset dependencies.
        config['pages'][0]['sections'] = [{'kind':'editorial','heading':'Selection','text':'Reviewed guidance.','reviewed_for_public':True,'claim_ids':['RW-NOT-APPROVED']}]
        sitekit.write(p/'content/site.json',config)
        rejected(lambda: build(p,True))
        assert sitekit.read(p/'private/latest-build.json')['status']=='NOT_READY'
        assert sitekit.read(p/'private/local-validation.json')['status']=='NOT_RUN'
        config['pages'][0]['sections'][0]['claim_ids']=[card['kb_id']]
        asset_path=p/'private/raw/synthetic.pdf';asset_path.write_bytes(b'%PDF-1.4\n% Synthetic pipeline fixture; not a real document\n%%EOF\n')
        asset={'asset_id':'fixture','company_id':meta['tenant_id'],'approval':'approved','visibility':'public',
               'rights_status':'owned','rights_evidence':'Test fixture created in this run',
               'file':'private/raw/synthetic.pdf','sha256':hashlib.sha256(asset_path.read_bytes()).hexdigest(),
               'claim_ids':['RW-NOT-APPROVED'],'is_ai_generated':False,'type':'download'}
        sitekit.write(p/'private/asset-register.json',[asset])
        config['pages'][0]['asset_ids']=['fixture'];sitekit.write(p/'content/site.json',config)
        rejected(lambda: build(p,True))
        asset['claim_ids']=[card['kb_id']];sitekit.write(p/'private/asset-register.json',[asset])
        for numeric_boolean in (1, 0, 1.0, 0.0):
            asset['is_ai_generated']=numeric_boolean;sitekit.write(p/'private/asset-register.json',[asset])
            rejected(lambda: build(p,True))
        asset['is_ai_generated']=False;sitekit.write(p/'private/asset-register.json',[asset])
        asset_site=build(p,True)
        assert (asset_site/'media/fixture.pdf').read_bytes()==asset_path.read_bytes()
        assert card['kb_id'] in sitekit.read(p/'content/page-manifest.json')[0]['claim_ids']
        asset_path.write_bytes(b'Changed unreviewed bytes')
        rejected(lambda: build(p,True))
        # Correct claim/hash references still cannot publish unsupported file types.
        asset_path=asset_path.rename(asset_path.with_suffix('.txt'))
        asset.update(file='private/raw/synthetic.txt',sha256=hashlib.sha256(asset_path.read_bytes()).hexdigest())
        sitekit.write(p/'private/asset-register.json',[asset])
        rejected(lambda: build(p,True))
        config['pages'][0]['asset_ids']=[];sitekit.write(p/'content/site.json',config)
        site=build(p,True)
        assert card['kb_id'] in sitekit.read(p/'content/page-manifest.json')[0]['claim_ids']
        # Broken file and anchor must fail for real, without any synthetic scoring.
        with (site/'index.html').open('a') as f:f.write('<a href="/missing/">broken</a><a href="/contact/#absent">anchor</a>')
        assert audit_site(site,True,'https://example.com')['status']=='FAIL'
        empty=root/'empty';empty.mkdir();assert audit_site(empty)['status']=='FAIL'
        card['status']='deprecated';sitekit.write(p/'private/knowledge-cards.json',cards)
        rejected(lambda: build(p,True))
        assert sitekit.read(p/'content/public-facts.json')==[]
        # Fresh directory builds never overwrite hand-edited previous output.
        rejected(lambda: build(p,False,site))
        for domain in ('https://evil.test/path','https://user:pass@evil.test','javascript:alert(1)','https://good.test/?q=x','https://-bad.test'):
            rejected(lambda: origin(domain))
        cli=Path(__file__).resolve().parents[1]/'scripts/orchestrator.py'
        cmd=[sys.executable,str(cli),'--name','CLI Test','--intro','Private intro','--industry','appliances','--out',str(root/'cli')]
        assert subprocess.run(cmd,capture_output=True).returncode==0
        assert subprocess.run(cmd,capture_output=True).returncode!=0
    print('PASS: 20 industry builds, draft/release checks, no private leakage, escaping, links, revoked facts, invalid origins, overwrite refusal, CLI exit codes')


if __name__=='__main__':run()
