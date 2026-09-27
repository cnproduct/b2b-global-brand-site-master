#!/usr/bin/env python3
"""Run with Python stdlib; optional argv[1] points to the installed validator."""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MODULE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'scripts/validate_site.py'
spec = importlib.util.spec_from_file_location('validator', MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
DOMAIN = 'https://example.com'


def fixture(root, release):
    root.mkdir()
    (root / 'products').mkdir()
    (root / 'css').mkdir()
    (root / 'css/site.css').write_text('body { color: #111; }')
    for slug in ('', 'products/'):
        schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Company products',
                  'description': 'Reviewed product information.', 'url': DOMAIN + '/' + slug, 'inLanguage': 'en'}
        markup = (f'<link rel="canonical" href="{schema["url"]}">'
                  f'<script type="application/ld+json">{json.dumps(schema)}</script>') if release else '<meta name="robots" content="noindex,nofollow">'
        (root / slug / 'index.html').write_text('<!doctype html><html lang="en"><head><title>Company products</title>'
            '<meta name="description" content="Reviewed product information.">' + markup
            + '<link rel="stylesheet" href="/css/site.css"></head><body><main id="main"><h1>Products</h1>'
            '<p>Reviewed product information.</p><a href="/products/#main">Products</a>'
            '<a href="https://unverified.example.com/">External</a></main></body></html>')
    locations = ''.join(f'<url><loc>{DOMAIN}/{slug}</loc></url>' for slug in ('', 'products/')) if release else ''
    (root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + locations + '</urlset>')
    (root / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + DOMAIN + '/sitemap.xml\n' if release else 'User-agent: *\nDisallow: /\n')


with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    for release in (False, True):
        site = root / ('release' if release else 'draft')
        fixture(site, release)
        result = validator.audit_site(site, release, DOMAIN if release else None)
        assert result['status'] == 'PASS', result
        assert result['external']['contact_delivery'] == 'NOT_RUN'
        assert result['external']['external_links'] == {'status': 'NOT_RUN', 'urls': ['https://unverified.example.com/']}
    empty = root / 'empty'
    empty.mkdir()
    assert validator.audit_site(empty)['status'] == 'FAIL'
    assert subprocess.run([sys.executable, str(MODULE), str(empty)], capture_output=True).returncode == 1
    site = root / 'release'
    assert validator.audit_site(site, True)['status'] == 'FAIL'
    assert validator.audit_site(site, True, 'example.com')['status'] == 'FAIL'
    source = (site / 'index.html').read_text()
    spaced = source.replace('Company products', 'Company  products').replace('Reviewed product information.', 'Reviewed  product information.')
    (site / 'index.html').write_text(spaced)
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'PASS'
    (site / 'index.html').write_text(source)
    for before, after in [
        ('<title>Company products</title>', ''),
        ('lang="en"', 'lang=""'),
        ('<h1>Products</h1>', ''),
        ('<main id="main">', '<div id="main">'),
        ('name="description"', 'name="ignored"'),
        ('/css/site.css', '/missing.css'),
        ('/products/#main', '/products/#missing'),
        ('/products/#main', '../../outside.html'),
        ('/products/#main', '/%2e%2e/outside.html'),
        ('/products/#main', 'java&#10;script:alert(1)'),
        ('/products/#main', 'https://user:password@example.com/products/'),
        ('rel="canonical" href="https://example.com/"', 'rel="canonical" href="https://wrong.example/"'),
        ('<head>', '<head><meta name="robots" content="noindex">'),
        ('"name": "Company products"', '"name": "Wrong company"'),
        ('"name": "Company products"', '"name": 1'),
        ('"description": "Reviewed product information."', '"description": "Invented promise."'),
        ('"inLanguage": "en"', '"inLanguage": "fr"'),
        ('"@context":', 'INVALID_JSON:'),
        ('"inLanguage": "en"', '"inLanguage": NaN'),
        ('<p>Reviewed product information.</p>', '<p>Something different.</p>'),
    ]:
        (site / 'index.html').write_text(source.replace(before, after))
        result = validator.audit_site(site, True, DOMAIN)
        assert result['status'] == 'FAIL', (before, after, result)
    (site / 'index.html').write_text(source)
    for name in ('export_kb.json', 'source_refs.json', '.env.production'):
        sensitive = site / name
        sensitive.write_text('{}')
        assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL', name
        sensitive.unlink()
    (site / 'public.json').write_text('{"source_refs": ["private/original"]}')
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL'
    (site / 'public.json').unlink()
    (site / 'raw').mkdir()
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL'
    (site / 'raw').rmdir()
    sitemap = (site / 'sitemap.xml').read_text()
    (site / 'sitemap.xml').write_text(sitemap.replace('<url><loc>https://example.com/products/</loc></url>', ''))
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL'
    (site / 'sitemap.xml').write_text(sitemap)
    robots = (site / 'robots.txt').read_text()
    (site / 'robots.txt').write_text(robots.replace('Allow: /', 'Allow: /\nDisallow: /products/'))
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL'
    (site / 'robots.txt').write_text(robots)
    (site / 'escape.html').symlink_to(root / 'draft/index.html')
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'FAIL'
    (site / 'escape.html').unlink()
    draft = root / 'draft'
    empty_sitemap = (draft / 'sitemap.xml').read_text()
    (draft / 'sitemap.xml').write_text(sitemap)
    assert validator.audit_site(draft)['status'] == 'FAIL'
    (draft / 'sitemap.xml').write_text(empty_sitemap)
    (draft / 'index.html').write_text((draft / 'index.html').read_text().replace('noindex,nofollow', 'index,follow'))
    assert validator.audit_site(draft)['status'] == 'FAIL'
    assert validator.audit_site(site, True, DOMAIN)['status'] == 'PASS'

print('Validator assertions passed.')
