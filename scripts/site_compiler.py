#!/usr/bin/env python3
"""Build a static preview/release from a reviewed content model and public facts."""
import hashlib
import html
import json
import os
import re
import shutil
import uuid
from pathlib import Path
from urllib.parse import urlsplit, quote
from xml.etree import ElementTree as ET
import sitekit
from extract_brand_dna import build_tokens, write_tokens_css

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*$')
EMAIL = re.compile(r'^[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$')


def e(value):
    return html.escape(str(value), quote=True)


def mailto(email):
    return 'mailto:' + quote(email, safe='@')


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
            'primary_color': None, 'logo_asset_id': None,
            'inquiry': {'mode': 'email_draft'}}


def inquiry_settings(config):
    inquiry = config.get('inquiry', {'mode': 'email_draft'})
    if not isinstance(inquiry, dict) or inquiry.get('mode') not in ('email_draft', 'http'):
        raise ValueError('inquiry mode must be email_draft or http')
    if inquiry['mode'] == 'http':
        endpoint = inquiry.get('endpoint', '')
        if not isinstance(endpoint, str) or not endpoint or re.search(r'[\s\\\x00-\x1f]', endpoint):
            raise ValueError('inquiry endpoint is missing or unsafe')
        if endpoint.startswith('/'):
            if not re.fullmatch(r'/(?!/)[A-Za-z0-9/_-]+', endpoint):
                raise ValueError('use a site-relative API path without query or fragments')
        else:
            parsed = urlsplit(endpoint)
            origin(parsed.scheme + '://' + parsed.netloc)
            if parsed.scheme != 'https' or parsed.query or parsed.fragment:
                raise ValueError('external inquiry endpoint must use HTTPS without query or fragment')
        if inquiry.get('endpoint_approved') is not True:
            raise ValueError('configure and approve the actual inquiry endpoint before enabling HTTP mode')
        if not isinstance(inquiry.get('privacy_notice'), str) or not inquiry['privacy_notice'].strip():
            raise ValueError('HTTP inquiry needs a reviewed notice describing the actual data use')
    return inquiry


def inquiry_html(email, inquiry):
    mode = inquiry['mode']
    if not email:
        return '<p>A contact route has not been configured for this preview.</p>'
    controls = []
    for name, label, kind, maximum, autocomplete in [
        ('name','Name','text',120,'name'), ('email','Email','email',254,'email'),
        ('company','Company (optional)','text',160,'organization'),
        ('country','Country / region (optional)','text',120,'country-name'),
        ('quantity','Quantity and unit (optional)','text',80,'off'),
        ('requirements','Product or project requirements','textarea',5000,'off')]:
        required = ' required' if name in ('name','email','requirements') else ''
        attrs = f'id="inquiry-{name}" name="{name}" maxlength="{maximum}" autocomplete="{autocomplete}" aria-describedby="error-{name}"{required}'
        field = f'<textarea {attrs} rows="5"></textarea>' if kind == 'textarea' else f'<input type="{kind}" {attrs}>'
        controls.append(f'<div class="field"><label for="inquiry-{name}">{label}</label>{field}<p class="field-error" id="error-{name}" data-error-for="{name}"></p></div>')
    action = inquiry['endpoint'] if mode == 'http' else mailto(email)
    label = 'Send inquiry' if mode == 'http' else 'Open email draft'
    notice = inquiry['privacy_notice'] if mode == 'http' else 'Your details will be included in your email draft. Review and send it in your email application.'
    return ('<section id="inquiry" class="inquiry-panel"><div class="section-head"><h2>Start with your requirements</h2>'
            '<p>Share the product, application and constraints you already know. Quantity and company details are optional.</p></div>'
            f'<form data-inquiry-form data-mode="{mode}" data-recipient="{e(email)}" action="{e(action)}" method="post">' + ''.join(controls) +
            '<div hidden><label for="inquiry-website">Leave this field empty</label><input id="inquiry-website" name="website" tabindex="-1" autocomplete="off"></div>'
            f'<p class="privacy-note">{e(notice)}</p><button type="submit" disabled data-requires-js>{label}</button>'
            '<p class="form-status" data-form-status role="status" aria-live="polite"></p></form>'
            f'<p>Prefer email? <a href="{e(mailto(email))}">{e(email)}</a></p>'
            '<noscript><p>The guided inquiry requires JavaScript. Use the email link above to contact us directly.</p></noscript></section>'
            '<script type="module" src="/js/inquiry.js"></script>')


def asset_figure(item, hero=False):
    path, url, asset = item
    caption = '<figcaption>AI-generated illustration; not documentary evidence.</figcaption>' if asset['is_ai_generated'] else ''
    dimensions = ''
    if any(asset.get(key) is not None for key in ('width', 'height')):
        if any(type(asset.get(key)) is not int or not 0 < asset[key] <= 30000 for key in ('width','height')):
            raise ValueError('image dimensions must be positive integer pixels')
        dimensions = f' width="{asset["width"]}" height="{asset["height"]}"'
    loading = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return f'<figure class="{"hero-media" if hero else "asset-figure"}"><img {loading}{dimensions} src="{url}" alt="{e(asset.get("alt_text") or asset["asset_id"])}">{caption}</figure>'


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


def protection_bundle(project, destination, meta, inquiry):
    """Default edge deployment, separate from the public directory and private sources."""
    paths = set()
    for file in destination.rglob('*'):
        if file.is_file():
            path = '/' + file.relative_to(destination).as_posix()
            paths.add(path)
            if path.endswith('/index.html'):
                directory = path[:-10]
                paths.add(directory)
                if directory != '/':
                    paths.add(directory.rstrip('/'))
            elif path.endswith('.html') and path != '/index.html':
                clean = path[:-5]
                paths.add(clean)
                paths.add(clean + '/')
    endpoint = inquiry.get('endpoint', '') if inquiry['mode'] == 'http' else ''
    inquiry_path = endpoint if endpoint.startswith('/') else None
    if inquiry_path in paths:
        raise ValueError('inquiry endpoint conflicts with a public page or asset')
    directory = project / 'private/deploy' / ('edge-' + uuid.uuid4().hex[:12])
    directory.mkdir(parents=True)
    site_id = hashlib.sha256(meta['tenant_id'].encode()).hexdigest()[:12]
    sitekit.write(directory/'policy.json', {'siteId': site_id, 'paths': sorted(paths), 'inquiryPath': inquiry_path})
    shutil.copy2(ROOT/'templates/edge-worker.mjs', directory/'worker.mjs')
    sitekit.write(directory/'wrangler.json', {
        'name': 'b2b-site-' + site_id, 'main': 'worker.mjs', 'compatibility_date': '2026-09-25',
        'assets': {'directory': os.path.relpath(destination, directory), 'binding': 'ASSETS',
                   'run_worker_first': True, 'html_handling': 'auto-trailing-slash', 'not_found_handling': 'none'},
        'ratelimits': [
            {'name': name, 'namespace_id': str(int(site_id, 16) * 2 + index + 1),
             'simple': {'limit': limit, 'period': 60}}
            for index, (name, limit) in enumerate([('READ_LIMITER', 300), ('INQUIRY_LIMITER', 5)])]})
    shutil.copy2(ROOT/'references/site-protection.md', directory/'DEPLOY.md')
    sitekit.write(project/'private/protection-status.json', {
        'default_enabled': True, 'configuration': 'GENERATED', 'runtime': 'NOT_RUN',
        'deployment_directory': str(directory), 'site_directory': str(destination),
        'provider': 'cloudflare-workers', 'external_inquiry_protection': 'NOT_RUN' if endpoint and not inquiry_path else 'NOT_APPLICABLE'})
    return directory


def build(project, release=False, site_out=None):
    project = Path(project).resolve()
    sitekit.write(project / 'private/latest-build.json', {'status': 'NOT_READY'})
    sitekit.write(project / 'private/local-validation.json', {'status': 'NOT_RUN'})
    sitekit.write(project / 'private/protection-status.json', {'configuration': 'NOT_READY', 'runtime': 'NOT_RUN'})
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
    inquiry = inquiry_settings(config)
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
        if page.get('hero_asset_id'):
            used_assets.add(page['hero_asset_id'])
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
            elif section.get('kind') == 'links':
                if not isinstance(section.get('items'), list) or not section['items']:
                    raise ValueError('link sections need a nonempty items array')
                if release and section.get('reviewed_for_public') is not True:
                    raise ValueError('link descriptions need editorial review')
                for item in section['items']:
                    if item.get('slug') not in slugs or not all(isinstance(item.get(k), str) and item[k].strip() for k in ('label','description')):
                        raise ValueError('link cards need an existing page slug, label and description')
                    check_claims(item.get('claim_ids', []), facts)
            else:
                raise ValueError('section kind must be facts, specifications, editorial or links')
    items = sitekit.read(project / 'private/asset-register.json')
    register = {a['asset_id']: a for a in items}
    if len(items) != len(register):
        raise ValueError('duplicate asset IDs')
    assets = assets_for(project, used_assets, register, meta['tenant_id'], facts)
    selected_logo = assets.get(config.get('logo_asset_id'))
    if selected_logo and selected_logo[0].suffix.lower() == '.pdf':
        raise ValueError('logo cannot be a PDF')
    for page in pages:
        if page.get('hero_asset_id') and assets[page['hero_asset_id']][0].suffix.lower() == '.pdf':
            raise ValueError('hero media must be a reviewed image, not a PDF')
    raw_logos = list((project / 'private/raw').glob('logo.*'))
    tokens = build_tokens(str(selected_logo[0]) if selected_logo else (str(raw_logos[0]) if raw_logos else None), meta['company'], config.get('primary_color'))
    destination = Path(site_out).resolve() if site_out else project / 'builds' / ('site-' + uuid.uuid4().hex[:12])
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'css').mkdir()
    write_tokens_css(tokens, destination / 'css/tokens.css', language, layout)
    shutil.copy2(ROOT / 'templates/assets/css/b2b-industrial-core.css', destination / 'css/site.css')
    if assets:
        (destination / 'media').mkdir()
    for path, url, asset in assets.values():
        shutil.copy2(path, destination / url.lstrip('/'))
    urls = {p['slug']: '/' + p['slug'].strip('/') + '/' if p['slug'] else '/' for p in pages}
    contact_page = next((p for p in pages if p['type'] == 'contact'), None)
    contact_url = urls[contact_page['slug']] + '#inquiry' if contact_page and email else (urls[contact_page['slug']] if contact_page else (mailto(email) if email else None))
    navigation = [p for p in pages if p.get('in_navigation', True)]
    draft_banner = '' if release else '<aside class="preview">Draft preview · Editorial and company facts require review before publication.</aside>'
    brand = (f'<img class="brand-mark" src="{selected_logo[1]}" alt="{e(meta["company"])}">' if selected_logo else e(meta['company']))
    manifest = []
    for page in pages:
        inquiry_url = contact_url
        if page['type'] == 'product' and contact_page and email:
            inquiry_url = urls[contact_page['slug']] + '?product=' + quote(page['heading'], safe='') + '#inquiry'
        nav = ''.join(f'<a href="{urls[p["slug"]]}"' + (' aria-current="page"' if p['slug'] == page['slug'] else '') + f'>{e(p["title"].split(" | ")[0])}</a>' for p in navigation)
        content, claim_ids = [], list(page.get('claim_ids', []))
        page_assets = list(dict.fromkeys(page.get('asset_ids', []) + ([page['hero_asset_id']] if page.get('hero_asset_id') else [])))
        for aid in page_assets:
            claim_ids.extend(assets[aid][2].get('claim_ids', []))
        if selected_logo:
            claim_ids.extend(selected_logo[2].get('claim_ids', []))
        section_links = []
        for index, section in enumerate(page['sections']):
            section_id = 'section-' + str(index + 1)
            section_links.append(f'<a href="#{section_id}">{e(section["heading"])}</a>')
            claim_ids.extend(section.get('claim_ids', []))
            if section['kind'] in ('facts', 'specifications'):
                body = ''.join(f'<article><h3>{e(facts[c]["title"])}</h3><p>{e(facts[c]["conclusion"])}</p>' +
                               (f'<p class="conditions">{e(facts[c]["conditions"])}</p>' if facts[c]['conditions'] else '') + '</article>' for c in section['claim_ids'])
                if section['kind'] == 'specifications':
                    body = '<div class="table-scroll" tabindex="0" role="region" aria-label="Specifications"><table><thead><tr><th>Parameter</th><th>Value</th><th>Conditions</th></tr></thead><tbody>' + ''.join(f'<tr><th scope="row">{e(facts[c]["title"])}</th><td>{e(facts[c]["conclusion"])}</td><td>{e(facts[c]["conditions"])}</td></tr>' for c in section['claim_ids']) + '</tbody></table></div>'
            elif section['kind'] == 'links':
                cards = []
                for item in section['items']:
                    claim_ids.extend(item.get('claim_ids', []))
                    cards.append(f'<a class="link-card" href="{urls[item["slug"]]}"><h3>{e(item["label"])}</h3><p>{e(item["description"])}</p><span aria-hidden="true">↗</span></a>')
                body = '<div class="link-grid">' + ''.join(cards) + '</div>'
            else:
                body = '<p>' + e(section['text']).replace('\n', '<br>') + '</p>'
            content.append(f'<section id="{section_id}"><div class="section-head"><h2>{e(section["heading"])}</h2></div>{body}</section>')
        if not page['sections']:
            content.append('<section><h2>Content in preparation</h2><p>Product information and supporting documents will be added after review.</p></section>')
        for aid in page.get('asset_ids', []):
            if aid == page.get('hero_asset_id'):
                continue
            path, url, asset = assets[aid]
            if path.suffix.lower() == '.pdf':
                content.append(f'<p><a href="{url}">Download {e(asset.get("alt_text") or aid)} (PDF)</a></p>')
            else:
                content.append(asset_figure(assets[aid]))
        if page.get('estimator') is True:
            (destination / 'js').mkdir(exist_ok=True)
            shutil.copy2(ROOT / 'templates/assets/js/sourcing_estimator.js', destination / 'js/sourcing_estimator.js')
            fields = [('quantity','Quantity (whole units)'),('unitVolumeM3','Packed volume per unit (m³)'),('unitWeightKg','Gross weight per unit (kg)'),('usableVolumeM3','Usable container volume (m³)'),('payloadKg','Permitted payload (kg)')]
            controls = ''.join(f'<label for="{name}">{label}</label><input id="{name}" name="{name}" type="number" min="{0 if name=="quantity" else "0.000001"}" step="{1 if name=="quantity" else "any"}" required>' for name,label in fields)
            content.append('<section><h2>Container capacity estimate</h2><p>Enter verified packing and route-specific limits. This is a capacity lower bound, not a packing plan or freight quote.</p><form data-load-estimator>' + controls + '<button type="submit">Estimate capacity</button><output aria-live="polite"></output></form><script type="module" src="/js/sourcing_estimator.js"></script></section>')
        if page['type'] == 'contact':
            if email:
                (destination / 'js').mkdir(exist_ok=True)
                shutil.copy2(ROOT / 'templates/assets/js/inquiry.js', destination / 'js/inquiry.js')
            content.append(inquiry_html(email, inquiry))
        elif contact_url:
            content.append(f'<section class="inquiry-panel"><div class="section-head"><h2>Discuss your requirements</h2><p>Include the product or application and any specifications you already have.</p></div><a class="button" href="{e(inquiry_url)}">Start an inquiry</a></section>')
        actions = []
        if contact_url:
            actions.append(f'<a class="button" href="{e(inquiry_url)}">Discuss your project</a>')
        secondary = next((p for p in pages if p['slug'] == 'products' and p['slug'] != page['slug']), None)
        if secondary:
            actions.append(f'<a class="button secondary" href="{urls[secondary["slug"]]}">Explore products</a>')
        hero_aside = asset_figure(assets[page['hero_asset_id']], True) if page.get('hero_asset_id') else (
            '<aside class="hero-aside"><h2>Explore</h2>' + ''.join(f'<a href="{urls[p["slug"]]}">{e(p["title"].split(" | ")[0])}<span aria-hidden="true">↗</span></a>' for p in navigation if p['slug'] != page['slug']) + '</aside>')
        hero = '<div class="hero"><div class="hero-copy"><p class="eyebrow">' + e(meta['company']) + '</p><h1>' + e(page['heading']) + '</h1><p class="lede">' + e(page['description']) + '</p><div class="actions">' + ''.join(actions) + '</div></div>' + hero_aside + '</div>'
        section_nav = '<nav class="section-nav" aria-label="On this page">' + ''.join(section_links) + '</nav>' if len(section_links) > 1 else ''
        header_action = f'<a class="button header-action" href="{e(inquiry_url)}">Contact</a>' if contact_url else ''
        canonical = f'<link rel="canonical" href="{domain}{urls[page["slug"]]}">' if release else ''
        schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': page['title'], 'description': page['description'], 'inLanguage': language}
        if release:
            schema['url'] = domain + urls[page['slug']]
            schema['publisher'] = {'@type': 'Organization', 'name': meta['company'], 'url': domain}
        schema_html = f'<script type="application/ld+json">{json_script(schema)}</script>' if release else ''
        robot = '' if release else '<meta name="robots" content="noindex,nofollow">'
        page_dir = destination / page['slug'];page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / 'index.html').write_text(f'''<!doctype html>
<html lang="{e(language)}" dir="{'rtl' if language.split('-')[0].lower() in ('ar','fa','he','ur') else 'ltr'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(page['title'])}</title><meta name="description" content="{e(page['description'])}">{robot}{canonical}
<link rel="stylesheet" href="/css/tokens.css"><link rel="stylesheet" href="/css/site.css">{schema_html}</head>
<body><a class="skip" href="#main">Skip to content</a>{draft_banner}<header><a class="brand" href="/">{brand}</a><nav aria-label="Main navigation">{nav}</nav>{header_action}</header>
<main id="main" tabindex="-1" data-layout="{layout}">{hero}{section_nav}{''.join(content)}</main>
<footer><p>© {e(meta['company'])}</p>{f'<a href="{e(mailto(email))}">{e(email)}</a>' if email else ''}</footer></body></html>''', encoding='utf-8')
        manifest.append({'url': urls[page['slug']], 'type': page['type'], 'language': language, 'claim_ids': sorted(set(claim_ids)), 'asset_ids': sorted(set(page_assets + ([config['logo_asset_id']] if selected_logo else []))), 'status': 'release' if release else 'draft'})
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
    design = project / 'DESIGN.md'
    if not design.exists():
        profile = sitekit.read(project / 'industry.json')
        design.write_text('# Website design direction · editable proposal\n\n'
            f'Company: {meta["company"]}\n\nAudience: {", ".join(profile["buyers"])}\n\n'
            f'Buyer journey: {profile["decision_path"]}\n\nVisual direction: {profile["visual_direction"]}\n\n'
            f'Layout: {layout}; language: {language}; primary action: discuss requirements.\n\n'
            f'Primary color: {tokens["colors"]["primary"]} ({tokens["color_source"]}).\n\n'
            'Use approved product media, technical detail and clear internal links. No invented proof.\n\n'
            'Typography: local/system fallbacks, fluid display and section roles, language-aware reading widths.\n\n'
            'Review 320/390/768/1440 widths, text resizing, keyboard path and inquiry errors before release.\n'
            'Browser, inquiry backend, inbox delivery and conversion validation: NOT_RUN.\n', encoding='utf-8')
    deployment = protection_bundle(project, destination, meta, inquiry)
    sitekit.write(project/'private/latest-build.json', {'status':'BUILT_UNVALIDATED', 'directory':str(destination), 'deployment_directory':str(deployment), 'release':release, 'domain':domain, 'page_count':len(pages)})
    return destination
