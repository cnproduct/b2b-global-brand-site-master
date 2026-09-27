#!/usr/bin/env python3
"""Build a static preview/release from a reviewed content model and public facts."""
import hashlib
import html
import json
import re
import shutil
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
import sitekit
from extract_brand_dna import build_tokens, write_tokens_css

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*$')
EMAIL = re.compile(r'^[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$')


def e(value):
    return html.escape(str(value), quote=True)


def json_script(value):
    return json.dumps(value, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')


def origin(value):
    if not value:
        return None
    parsed = urlsplit(value if '://' in value else 'https://' + value)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('domain must be an HTTPS origin without path, credentials, query or fragment')
    host = (parsed.hostname or '').encode('idna').decode('ascii').lower()
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host) or '.' not in host or '..' in host or parsed.port:
        raise ValueError('invalid domain; use the intended public hostname')
    if any(not label or len(label) > 63 or label.startswith('-') or label.endswith('-') for label in host.split('.')):
        raise ValueError('invalid domain label')
    return 'https://' + host


def starter(project):
    """Editable six-page briefs, deliberately without invented company capabilities."""
    meta = sitekit.read(project / 'project.json')
    pages = []
    for slug, title, heading in [('', 'Home', 'Products, specifications and sourcing support'),
        ('products', 'Products', 'Explore product requirements'), ('capabilities', 'Capabilities', 'Capabilities and quality information'),
        ('resources', 'Resources', 'Technical resources'), ('oem-odm', 'OEM / ODM', 'Discuss your development requirements'),
        ('contact', 'Contact', 'Tell us about your requirements')]:
        pages.append({'slug': slug, 'type': 'contact' if slug == 'contact' else ('home' if not slug else 'collection'),
                      'title': title + ' | ' + meta['company'], 'description': heading + '.',
                      'heading': heading, 'reviewed_for_public': False,
                      'sections': [], 'asset_ids': [], 'estimator': False})
    return {'pages': pages, 'llms': False, 'training_bot_policy': 'unspecified',
            'primary_color': None, 'logo_asset_id': None}


def assets_for(project, ids, register, tenant, facts):
    result = {}
    for aid in ids:
        asset = register.get(aid)
        if not isinstance(asset, dict) or not re.fullmatch(r'[a-zA-Z0-9_-]+', aid):
            raise ValueError('unknown/unsafe asset ID: ' + str(aid))
        if asset.get('company_id') != tenant or asset.get('approval') != 'approved' or asset.get('visibility') != 'public':
            raise ValueError('asset is not approved public content: ' + aid)
        if asset.get('rights_status') not in ('owned', 'licensed', 'permission_granted') or not asset.get('rights_evidence'):
            raise ValueError('asset rights are incomplete: ' + aid)
        check_claims(asset.get('claim_ids', []), facts)
        if type(asset.get('is_ai_generated')) is not bool:
            raise ValueError('asset needs explicit AI provenance: ' + aid)
        if asset.get('is_ai_generated') is True and asset.get('type') in ('certificate', 'test_report', 'factory_photo', 'customer_case'):
            raise ValueError('generated image cannot impersonate evidence: ' + aid)
        path = (project / asset['file']).resolve()
        if not path.is_relative_to(project.resolve()) or not path.is_file():
            raise ValueError('asset path escapes project or is missing')
        suffix = path.suffix.lower()
        if suffix not in ('.png', '.jpg', '.jpeg', '.webp', '.pdf'):
            raise ValueError('public asset must be raster/PDF; sanitize/rasterize SVG separately')
        if hashlib.sha256(path.read_bytes()).hexdigest() != asset.get('sha256'):
            raise ValueError('asset hash changed: ' + aid)
        result[aid] = (path, '/media/' + aid + suffix, asset)
    return result


def check_claims(claims, facts):
    if not isinstance(claims, list) or any(not isinstance(c, str) or c not in facts for c in claims):
        raise ValueError('reference to unavailable or revoked facts')


def build(project, release=False, site_out=None):
    project = Path(project).resolve()
    sitekit.write(project / 'private/latest-build.json', {'status': 'NOT_READY'})
    sitekit.write(project / 'private/local-validation.json', {'status': 'NOT_RUN'})
    (project / 'acceptance.md').write_text('# Build status\n\nNOT_READY: current inputs have not passed a new build and validation.\n', encoding='utf-8')
    meta = sitekit.read(project / 'project.json')
    layout = sitekit.read(project / 'industry.json').get('layout', 'engineering')
    if layout not in ('engineering', 'materials', 'oem', 'evidence'):
        raise ValueError('unknown layout')
    config = sitekit.read(project / 'content/site.json')
    domain = origin(meta.get('domain'))
    email = meta.get('contact')
    if email and (not isinstance(email, str) or not EMAIL.fullmatch(email)):
        raise ValueError('invalid contact email')
    language = meta.get('language', 'en')
    if not isinstance(language, str) or not re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', language):
        raise ValueError('invalid language tag')
    pages = config.get('pages')
    if not isinstance(pages, list) or not pages:
        raise ValueError('site needs a nonempty pages array')
    slugs = [p.get('slug') for p in pages]
    if len(set(slugs)) != len(slugs) or '' not in slugs or any(s != '' and (not isinstance(s, str) or not SLUG.fullmatch(s)) for s in slugs):
        raise ValueError('unique safe slugs including the homepage are required')
    if config.get('training_bot_policy', 'unspecified') not in ('unspecified', 'allow', 'disallow'):
        raise ValueError('unknown training bot policy')
    if release and (not domain or not email or meta.get('identity_approved') is not True or meta.get('contact_approved') is not True):
        raise ValueError('release requires approved identity/contact and an explicit domain/email')
    sitekit.export(project)  # Never reuse stale public facts after source changes.
    facts = {c['kb_id']: c for c in sitekit.read(project / 'content/public-facts.json')}
    if release and not facts:
        raise ValueError('release requires at least one approved company fact')
    used_assets = set()
    if config.get('logo_asset_id'):
        used_assets.add(config['logo_asset_id'])
    for page in pages:
        if release and page.get('reviewed_for_public') is not True:
            raise ValueError('page editorial review missing: ' + page['slug'])
        for key in ('title', 'description', 'heading'):
            if not isinstance(page.get(key), str) or not page[key].strip():
                raise ValueError('missing page ' + key)
        sections = page.get('sections')
        if not isinstance(sections, list) or (release and not sections):
            raise ValueError('release pages need useful reviewed sections')
        used_assets.update(page.get('asset_ids', []))
        check_claims(page.get('claim_ids', []), facts)
        for section in sections:
            check_claims(section.get('claim_ids', []), facts)
            if not isinstance(section.get('heading'), str):
                raise ValueError('section heading required')
            if section.get('kind') in ('facts', 'specifications'):
                claims = section.get('claim_ids')
                if not isinstance(claims, list) or not claims or any(c not in facts for c in claims):
                    raise ValueError('fact section references unavailable or revoked facts')
            elif section.get('kind') == 'editorial':
                if not isinstance(section.get('text'), str) or not section['text'].strip():
                    raise ValueError('editorial text required')
                if release and section.get('reviewed_for_public') is not True:
                    raise ValueError('editorial section needs review')
            else:
                raise ValueError('section kind must be facts, specifications or editorial')
    items = sitekit.read(project / 'private/asset-register.json')
    register = {a['asset_id']: a for a in items}
    if len(items) != len(register):
        raise ValueError('duplicate asset IDs')
    assets = assets_for(project, used_assets, register, meta['tenant_id'], facts)
    selected_logo = assets.get(config.get('logo_asset_id'))
    if selected_logo and selected_logo[0].suffix.lower() == '.pdf':
        raise ValueError('logo cannot be a PDF')
    raw_logos = list((project / 'private/raw').glob('logo.*'))
    tokens = build_tokens(str(selected_logo[0]) if selected_logo else (str(raw_logos[0]) if raw_logos else None), meta['company'], config.get('primary_color'))
    destination = Path(site_out).resolve() if site_out else project / 'builds' / ('site-' + uuid.uuid4().hex[:12])
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'css').mkdir()
    write_tokens_css(tokens, destination / 'css/tokens.css')
    shutil.copy2(ROOT / 'templates/assets/css/b2b-industrial-core.css', destination / 'css/site.css')
    if assets:
        (destination / 'media').mkdir()
    for path, url, asset in assets.values():
        shutil.copy2(path, destination / url.lstrip('/'))
    urls = {p['slug']: '/' + p['slug'].strip('/') + '/' if p['slug'] else '/' for p in pages}
    nav = ''.join(f'<a href="{urls[p["slug"]]}">{e(p["title"].split(" | ")[0])}</a>' for p in pages)
    draft_banner = '' if release else '<aside class="preview">Draft preview · Editorial and company facts require review before publication.</aside>'
    brand = (f'<img class="brand-mark" src="{selected_logo[1]}" alt="{e(meta["company"])}">' if selected_logo else e(meta['company']))
    manifest = []
    for page in pages:
        content, claim_ids = [], list(page.get('claim_ids', []))
        for aid in page.get('asset_ids', []):
            claim_ids.extend(assets[aid][2].get('claim_ids', []))
        if selected_logo:
            claim_ids.extend(selected_logo[2].get('claim_ids', []))
        for section in page['sections']:
            claim_ids.extend(section.get('claim_ids', []))
            if section['kind'] in ('facts', 'specifications'):
                body = ''.join(f'<article><h3>{e(facts[c]["title"])}</h3><p>{e(facts[c]["conclusion"])}</p>' +
                               (f'<p class="conditions">{e(facts[c]["conditions"])}</p>' if facts[c]['conditions'] else '') + '</article>' for c in section['claim_ids'])
                if section['kind'] == 'specifications':
                    body = '<div class="table-scroll" tabindex="0" role="region" aria-label="Specifications"><table><thead><tr><th>Parameter</th><th>Value</th><th>Conditions</th></tr></thead><tbody>' + ''.join(f'<tr><th scope="row">{e(facts[c]["title"])}</th><td>{e(facts[c]["conclusion"])}</td><td>{e(facts[c]["conditions"])}</td></tr>' for c in section['claim_ids']) + '</tbody></table></div>'
            else:
                body = '<p>' + e(section['text']).replace('\n', '<br>') + '</p>'
            content.append(f'<section><h2>{e(section["heading"])}</h2>{body}</section>')
        if not page['sections']:
            content.append('<section><h2>Content in preparation</h2><p>Product information and supporting documents will be added after review.</p></section>')
        for aid in page.get('asset_ids', []):
            path, url, asset = assets[aid]
            if path.suffix.lower() == '.pdf':
                content.append(f'<p><a href="{url}">Download {e(asset.get("alt_text") or aid)} (PDF)</a></p>')
            else:
                caption = '<figcaption>AI-generated illustration; not documentary evidence.</figcaption>' if asset.get('is_ai_generated') is True else ''
                content.append(f'<figure><img loading="lazy" src="{url}" alt="{e(asset.get("alt_text") or aid)}">{caption}</figure>')
        if page.get('estimator') is True:
            (destination / 'js').mkdir(exist_ok=True)
            shutil.copy2(ROOT / 'templates/assets/js/sourcing_estimator.js', destination / 'js/sourcing_estimator.js')
            fields = [('quantity','Quantity (whole units)'),('unitVolumeM3','Packed volume per unit (m³)'),('unitWeightKg','Gross weight per unit (kg)'),('usableVolumeM3','Usable container volume (m³)'),('payloadKg','Permitted payload (kg)')]
            controls = ''.join(f'<label for="{name}">{label}</label><input id="{name}" name="{name}" type="number" min="{0 if name=="quantity" else "0.000001"}" step="{1 if name=="quantity" else "any"}" required>' for name,label in fields)
            content.append('<section><h2>Container capacity estimate</h2><p>Enter verified packing and route-specific limits. This is a capacity lower bound, not a packing plan or freight quote.</p><form data-load-estimator>' + controls + '<button type="submit">Estimate capacity</button><output aria-live="polite"></output></form><script type="module" src="/js/sourcing_estimator.js"></script></section>')
        if page['type'] == 'contact':
            content.append(f'<p><a class="button" href="mailto:{e(email)}">Email your requirements</a></p>' if email else '<p>A contact route has not been configured for this preview.</p>')
        canonical = f'<link rel="canonical" href="{domain}{urls[page["slug"]]}">' if release else ''
        schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': page['title'], 'description': page['description'], 'inLanguage': language}
        if release:
            schema['url'] = domain + urls[page['slug']]
            schema['publisher'] = {'@type': 'Organization', 'name': meta['company'], 'url': domain}
        schema_html = f'<script type="application/ld+json">{json_script(schema)}</script>' if release else ''
        robot = '' if release else '<meta name="robots" content="noindex,nofollow">'
        page_dir = destination / page['slug'];page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / 'index.html').write_text(f'''<!doctype html>
<html lang="{e(language)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(page['title'])}</title><meta name="description" content="{e(page['description'])}">{robot}{canonical}
<link rel="stylesheet" href="/css/tokens.css"><link rel="stylesheet" href="/css/site.css">{schema_html}</head>
<body><a class="skip" href="#main">Skip to content</a>{draft_banner}<header><a class="brand" href="/">{brand}</a><nav aria-label="Main navigation">{nav}</nav></header>
<main id="main" tabindex="-1" data-layout="{layout}"><div class="intro"><p class="eyebrow">{e(meta['company'])}</p><h1>{e(page['heading'])}</h1><p>{e(page['description'])}</p></div>{''.join(content)}</main>
<footer><p>{e(meta['company'])}</p>{f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else ''}</footer></body></html>''', encoding='utf-8')
        manifest.append({'url': urls[page['slug']], 'type': page['type'], 'language': language, 'claim_ids': sorted(set(claim_ids)), 'asset_ids': page.get('asset_ids', []), 'status': 'release' if release else 'draft'})
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    if release:
        for url in urls.values():
            ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = domain + url
    ET.ElementTree(sitemap).write(destination/'sitemap.xml', encoding='utf-8', xml_declaration=True)
    robots = 'User-agent: *\nAllow: /\n' if release else 'User-agent: *\nDisallow: /\n'
    if release:
        robots += '\nSitemap: ' + domain + '/sitemap.xml\n'
        policy = config.get('training_bot_policy')
        if policy in ('allow', 'disallow'):
            robots += '\nUser-agent: GPTBot\n' + ('Allow' if policy == 'allow' else 'Disallow') + ': /\n'
    (destination/'robots.txt').write_text(robots, encoding='utf-8')
    if release and config.get('llms') is True:
        (destination/'llms.txt').write_text('# ' + meta['company'].replace('\n',' ') + '\n\n> Public website navigation.\n\n## Pages\n\n' + '\n'.join('- [' + p['title'].replace('[','').replace(']','').replace('\n',' ') + '](' + domain + urls[p['slug']] + ')' for p in pages) + '\n', encoding='utf-8')
    sitekit.write(project/'content/page-manifest.json', manifest)
    sitekit.write(project/'private/brand-tokens.json', tokens)
    sitekit.write(project/'private/latest-build.json', {'status':'BUILT_UNVALIDATED', 'directory':str(destination), 'release':release, 'domain':domain, 'page_count':len(pages)})
    return destination
