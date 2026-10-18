#!/usr/bin/env python3
"""Single-page HTTP evidence probe; does not render JS or crawl the site."""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


class PageParser(HTMLParser):
    """Collect source HTML evidence shared by the probe and static checks."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''
        self.lang = ''
        self.meta = {}
        self.links = []
        self.images = []
        self.h1_count = 0
        self.schemas = []
        self._title = False
        self._schema = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
        elif tag == 'title':
            self._title = True
        elif tag == 'h1':
            self.h1_count += 1
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            value = a.get('content', '')
            self.meta[key] = ', '.join(filter(None, (self.meta.get(key), value))) if key in ('robots', 'googlebot', 'bingbot') else value
        elif tag == 'link':
            self.links.append(a)
        elif tag == 'img':
            self.images.append(a)
        elif tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self._schema = ''

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._schema is not None:
            self._schema += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self._title = False
        if tag == 'script' and self._schema is not None:
            self.schemas.append(self._schema)
            self._schema = None


def fetch(url):
    if urlsplit(url).scheme not in ('http', 'https'):
        raise ValueError('Only HTTP(S) URLs are supported')
    # ponytail: HTTP bodies capped at 10 MiB; browser harvest handles larger/dynamic assets.
    with urlopen(Request(url, headers={'User-Agent': 'RenWorkEvidenceProbe/3.0'}), timeout=20) as response:
        body = response.read(10 * 1024 * 1024 + 1)
        if len(body) > 10 * 1024 * 1024:
            raise ValueError('Response exceeds 10 MiB')
        return body, {
            'url': url, 'final_url': response.url, 'status': response.status,
            'content_type': response.headers.get_content_type(),
            'sha256': hashlib.sha256(body).hexdigest(),
            'charset': response.headers.get_content_charset() or 'utf-8',
        }, dict(response.headers)


def run_forensics(target_url, output_dir):
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Evidence directory must be empty; use a new capture directory')
    raw, record, headers = fetch(target_url)
    if record['content_type'] not in ('text/html', 'application/xhtml+xml'):
        raise ValueError('Target did not return HTML')
    parser = PageParser()
    parser.feed(raw.decode(record['charset'], errors='replace'))
    out.mkdir(parents=True, exist_ok=True)
    (out / 'homepage.html').write_bytes(raw)
    (out / 'headers.json').write_text(json.dumps(headers, indent=2))
    manifest = {'captured_at': datetime.now(timezone.utc).isoformat(), 'scope': 'single-page-http',
                'resources': [dict(record, file='homepage.html')], 'failures': []}
    seo = {'title': parser.title.strip(), 'lang': parser.lang, 'meta': parser.meta,
           'links': parser.links, 'schemas_raw': parser.schemas}
    (out / 'seo_metadata.json').write_text(json.dumps(seo, indent=2, ensure_ascii=False))
    resources = [(urljoin(record['final_url'], name), name, ('text/plain', 'application/xml', 'text/xml'))
                 for name in ('/robots.txt', '/sitemap.xml')]
    css = [urljoin(record['final_url'], a['href']) for a in parser.links
           if 'stylesheet' in a.get('rel', '').split() and a.get('href')]
    resources += [(url, f'css/bundle_{i}.css', ('text/css',)) for i, url in enumerate(dict.fromkeys(css))]
    for url, name, allowed in resources:
        try:
            data, item, _ = fetch(url)
            if item['content_type'] not in allowed:
                raise ValueError(f"Unexpected content type: {item['content_type']}")
            relative = name.lstrip('/')
            dest = out / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            manifest['resources'].append(dict(item, file=relative))
        except Exception as exc:
            manifest['failures'].append({'url': url, 'error': str(exc)})
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"HTTP capture: {out}; {len(manifest['resources'])} resources, {len(manifest['failures'])} gaps. Browser/full-site checks NOT_RUN.")
    return not manifest['failures']


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('url')
    cli.add_argument('output_dir')
    args = cli.parse_args()
    try:
        sys.exit(0 if run_forensics(args.url, args.output_dir) else 1)
    except Exception as exc:
        cli.exit(1, f'Probe failed: {exc}\n')
