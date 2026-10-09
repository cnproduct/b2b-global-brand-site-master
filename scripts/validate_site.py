#!/usr/bin/env python3
"""Offline checks for the static compiler output; no network or ranking claims."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree as ET


def normalized(text):
    return ' '.join(text.split())


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack, self.titles, self.headings, self.descriptions = [], [], [], []
        self.languages, self.canonicals, self.robots, self.schemas = [], [], [], []
        self.refs, self.ids, self.duplicate_ids, self.main_text = [], set(), set(), []
        self.main_count = 0
        self.schema_text = None
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append(tag)
        if tag == 'html':
            self.languages.append(attrs.get('lang', ''))
        if tag == 'title':
            self.titles.append([])
        if tag == 'h1':
            self.headings.append([])
        if tag == 'main':
            self.main_count += 1
        if tag == 'meta':
            name = attrs.get('name', '').lower()
            if name == 'description':
                self.descriptions.append(attrs.get('content', ''))
            if name in ('robots', 'googlebot', 'bingbot'):
                self.robots.append((name, attrs.get('content', '').lower()))
        if tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            self.canonicals.append(attrs.get('href', ''))
        if tag == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
            self.schema_text = []
        for anchor in {attrs.get('id'), attrs.get('name') if tag == 'a' else None}:
            if anchor:
                if anchor in self.ids:
                    self.duplicate_ids.add(anchor)
                self.ids.add(anchor)
        for attr in ('href', 'src'):
            if attr in attrs:
                self.refs.append((tag, attr, attrs[attr] or ''))

    def handle_endtag(self, tag):
        if tag == 'script' and self.schema_text is not None:
            self.schemas.append(''.join(self.schema_text))
            self.schema_text = None
        if tag in self.stack:
            del self.stack[len(self.stack) - 1 - self.stack[::-1].index(tag):]

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text.append(data)
        if 'title' in self.stack and self.titles:
            self.titles[-1].append(data)
        if not any(tag in self.stack for tag in ('script', 'style', 'template')):
            if 'h1' in self.stack and self.headings:
                self.headings[-1].append(data)
            if 'main' in self.stack:
                self.main_text.append(data)


def https_origin(value):
    if not isinstance(value, str) or re.search(r'\s', value):
        raise ValueError('domain must be an HTTPS origin without whitespace')
    parsed = urlsplit(value)
    host = (parsed.hostname or '').encode('idna').decode('ascii').lower()
    if (parsed.scheme != 'https' or not host or '.' not in host or parsed.username or parsed.password
            or parsed.port or parsed.query or parsed.fragment or parsed.path not in ('', '/')
            or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in host.split('.'))):
        raise ValueError('domain must be a complete HTTPS origin, without path, port, credentials, query or fragment')
    return 'https://' + host


def allowed_page_paths(relative):
    if relative.name == 'index.html':
        parent = relative.parent.as_posix()
        path = '/' + ('' if parent == '.' else parent)
        return [quote(path.rstrip('/') + '/', safe='/')]
    paths = []
    if relative.suffix.lower() in ('.html', '.htm'):
        parent = relative.parent.as_posix()
        stem = relative.stem
        clean_path = '/' + (stem if parent == '.' else f"{parent}/{stem}")
        paths.append(quote(clean_path, safe='/'))
    paths.append(quote('/' + relative.as_posix(), safe='/'))
    return paths


def page_path(relative):
    return allowed_page_paths(relative)[0]


def schema_nodes(value):
    if isinstance(value, list):
        for item in value:
            yield from schema_nodes(item)
    elif isinstance(value, dict):
        yield value
        if '@graph' in value:
            yield from schema_nodes(value['@graph'])


def reject_json_constant(value):
    raise ValueError('non-standard JSON numeric constant: ' + value)


def audit_site(site_dir, release=False, domain=None):
    root = Path(site_dir).resolve()
    errors = []
    checks = {key: {'status': 'PASS'} for key in ('files', 'html_metadata', 'internal_links', 'schema', 'indexing', 'public_boundary')}
    external_links = set()

    def fail(check, message):
        checks[check]['status'] = 'FAIL'
        errors.append(message)

    def report():
        return {'status': 'FAIL' if errors else 'PASS', 'errors': errors, 'checks': checks,
                'external': {'external_links': {'status': 'NOT_RUN', 'urls': sorted(external_links)},
                             'http_status_headers': 'NOT_RUN', 'browser_render': 'NOT_RUN',
                             'contact_delivery': 'NOT_RUN', 'search_indexing': 'NOT_RUN', 'geo_citations': 'NOT_RUN'}}

    try:
        domain = https_origin(domain) if domain else None
    except (ValueError, UnicodeError) as exc:
        fail('indexing', str(exc))
        domain = None
    if release and not domain:
        fail('indexing', 'Release validation requires --domain with the intended HTTPS origin.')
    if not root.is_dir():
        fail('files', 'Site directory does not exist.')
        return report()
    if not (root / 'index.html').is_file():
        fail('files', 'Missing homepage index.html.')
    paths = sorted(path for path in root.rglob('*') if path.is_file() and path.resolve().is_relative_to(root))
    html_paths = [path for path in paths if path.suffix.lower() in ('.html', '.htm')]
    checks['files']['html_pages'] = len(html_paths)
    if not html_paths:
        fail('files', 'No HTML pages found; an empty directory cannot pass.')
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if not path.resolve().is_relative_to(root):
            fail('public_boundary', f'{relative}: symlink escapes the site directory.')
            continue
        if any(part.lower() in ('private', 'raw', '.git')
               or part.lower().startswith('.env')
               or re.fullmatch(r'(export_kb|source_refs|asset-register)(\..+)?', part.lower()) for part in relative.parts):
            fail('public_boundary', f'{relative}: private/source material must not be in public output.')
        if path.is_file() and path.suffix.lower() in ('.html', '.htm', '.json', '.js', '.txt', '.md'):
            try:
                if re.search(r'["\'](?:source_refs|export_kb|private_notes|tenant_id)["\']\s*:', path.read_text(encoding='utf-8')):
                    fail('public_boundary', f'{relative}: internal source/tenant fields appear in public output.')
            except (OSError, UnicodeError) as exc:
                fail('files', f'{relative}: cannot read text file ({exc}).')
    pages = {}
    expected_urls = set()
    for path in html_paths:
        relative = path.relative_to(root)
        try:
            page = Page(path.read_text(encoding='utf-8'))
            pages[path.resolve()] = page
        except (OSError, UnicodeError, ValueError) as exc:
            fail('html_metadata', f'{relative}: cannot parse HTML ({exc}).')
            continue
        title = normalized(''.join(page.titles[0])) if page.titles else ''
        description = normalized(page.descriptions[0]) if page.descriptions else ''
        if len(page.titles) != 1 or not title:
            fail('html_metadata', f'{relative}: exactly one nonempty title is required.')
        if len(page.descriptions) != 1 or not description:
            fail('html_metadata', f'{relative}: exactly one nonempty meta description is required.')
        if len(page.languages) != 1 or not re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', page.languages[0]):
            fail('html_metadata', f'{relative}: a valid html lang is required.')
        if len(page.headings) != 1 or not normalized(''.join(page.headings[0])):
            fail('html_metadata', f'{relative}: exactly one nonempty H1 is required.')
        if page.main_count != 1 or not normalized(' '.join(page.main_text)):
            fail('html_metadata', f'{relative}: exactly one nonempty main is required.')
        if page.duplicate_ids:
            fail('html_metadata', f'{relative}: duplicate anchor IDs: {sorted(page.duplicate_ids)}.')
        directives = [(name, set(re.split(r'[\s,]+', content))) for name, content in page.robots]
        if release and any(tokens & {'noindex', 'none'} for _, tokens in directives):
            fail('indexing', f'{relative}: release page contains noindex/none.')
        if not release and not any(name == 'robots' and tokens & {'noindex', 'none'} for name, tokens in directives):
            fail('indexing', f'{relative}: draft page requires a robots noindex directive.')
        allowed_paths = allowed_page_paths(relative)
        expected_options = [domain + p for p in allowed_paths] if domain else []
        matched_canonical = None
        if release and expected_options:
            if page.canonicals and len(page.canonicals) == 1 and page.canonicals[0] in expected_options:
                matched_canonical = page.canonicals[0]
                expected_urls.add(matched_canonical)
            else:
                fail('indexing', f'{relative}: canonical must be one of {expected_options}, got {page.canonicals}.')
        webpage_nodes = []
        for payload in page.schemas:
            try:
                data = json.loads(payload, parse_constant=reject_json_constant)
                if not isinstance(data, (dict, list)):
                    raise ValueError('JSON-LD must be an object or array')
                for node in schema_nodes(data):
                    types = node.get('@type', [])
                    types = [types] if isinstance(types, str) else types
                    if isinstance(types, list) and any(t in ('WebPage', 'https://schema.org/WebPage', 'http://schema.org/WebPage') for t in types):
                        webpage_nodes.append(node)
            except (ValueError, TypeError) as exc:
                fail('schema', f'{relative}: invalid JSON-LD ({exc}).')
        if page.schema_text is not None:
            fail('schema', f'{relative}: unterminated JSON-LD script.')
        if release and not webpage_nodes:
            fail('schema', f'{relative}: release output requires a WebPage JSON-LD node.')
        for node in webpage_nodes:
            if (not all(isinstance(node.get(key), str) for key in ('name', 'description'))
                    or normalized(node['name']) != title or normalized(node['description']) != description):
                fail('schema', f'{relative}: WebPage name/description must match page metadata.')
            if node.get('inLanguage') != (page.languages[0] if page.languages else None):
                fail('schema', f'{relative}: WebPage inLanguage must match html lang.')
            if release and matched_canonical and node.get('url') != matched_canonical:
                fail('schema', f'{relative}: WebPage url must match the canonical URL ({matched_canonical}).')
            if description and description not in normalized(''.join(page.main_text)):
                fail('schema', f'{relative}: schema description must also be present in visible main content.')
    checked_links = 0
    for path, page in pages.items():
        relative = path.relative_to(root)
        for tag, attr, value in page.refs:
            checked_links += 1
            try:
                if re.match(r'javascript:', re.sub(r'[\x00-\x20]', '', value), re.I):
                    raise ValueError('javascript URLs are forbidden')
                parsed = urlsplit(value.strip())
                if parsed.username or parsed.password:
                    raise ValueError('URL credentials must not be published')
                if parsed.scheme and parsed.scheme not in ('http', 'https', 'mailto', 'tel'):
                    raise ValueError('unsupported URL scheme')
                if parsed.scheme in ('http', 'https') and not parsed.netloc:
                    raise ValueError('HTTP URLs require a hostname')
                if tag == 'base':
                    raise ValueError('base href is unsupported; use explicit site-relative URLs')
                if parsed.scheme in ('mailto', 'tel'):
                    continue
                if parsed.netloc:
                    reference_origin = (parsed.scheme or 'https') + '://' + parsed.netloc.lower()
                    if reference_origin != domain:
                        external_links.add(value)
                        continue
                decoded = unquote(parsed.path, errors='strict')
                if '\\' in decoded or '\x00' in decoded:
                    raise ValueError('unsafe path separator or null byte')
                if not decoded and not parsed.netloc:
                    target = path
                elif decoded.startswith('/') or parsed.netloc:
                    target = root / decoded.lstrip('/')
                else:
                    target = path.parent / decoded
                if target.is_dir():
                    if (target / 'index.html').is_file():
                        target /= 'index.html'
                    elif target.with_suffix('.html').is_file():
                        target = target.with_suffix('.html')
                    else:
                        target /= 'index.html'
                elif not target.is_file():
                    alt = target.parent / target.name.rstrip('/') if target.name else target
                    if alt.with_suffix('.html').is_file():
                        target = alt.with_suffix('.html')
                    elif (target / 'index.html').is_file():
                        target = target / 'index.html'
                target = target.resolve()
                if not target.is_relative_to(root):
                    raise ValueError('path escapes the site directory')
                if not target.is_file():
                    raise ValueError('target file does not exist')
                if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                    raise ValueError('target HTML anchor does not exist')
            except (ValueError, OSError, UnicodeError) as exc:
                fail('internal_links', f'{relative}: {attr}={value!r}: {exc}.')
    checks['internal_links']['references'] = checked_links
    try:
        tree = ET.parse(root / 'sitemap.xml')
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        if tree.getroot().tag != namespace + 'urlset':
            raise ValueError('sitemap root must be the standard namespaced urlset')
        entries = tree.getroot().findall(namespace + 'url')
        if any(len(entry.findall(namespace + 'loc')) != 1 for entry in entries):
            raise ValueError('each sitemap URL requires exactly one loc element')
        locations = [entry.findtext(namespace + 'loc', default='').strip() for entry in entries]
        if any(not value for value in locations) or len(locations) != len(set(locations)):
            raise ValueError('sitemap contains missing or duplicate URLs')
        if release and set(locations) != expected_urls:
            raise ValueError('sitemap URL set must equal the canonical URL set of all HTML pages')
        if not release and locations:
            raise ValueError('draft sitemap must have no URLs')
    except (OSError, ET.ParseError, ValueError) as exc:
        fail('indexing', f'sitemap.xml: {exc}.')
    try:
        robot_lines = (root / 'robots.txt').read_text(encoding='utf-8').splitlines()
        groups, agents, rules, sitemaps = [], [], [], []
        for line in robot_lines + ['User-agent: __end__']:
            line = line.split('#', 1)[0].strip()
            if not line or ':' not in line:
                continue
            key, value = [part.strip() for part in line.split(':', 1)]
            key = key.lower()
            if key == 'sitemap':
                sitemaps.append(value)
            elif key == 'user-agent':
                if rules:
                    groups.append((agents, rules))
                    agents, rules = [], []
                agents.append(value.lower())
            elif key in ('allow', 'disallow'):
                rules.append((key, value))
        wildcard = [rule for user_agents, rules in groups if '*' in user_agents for rule in rules]
        if not wildcard:
            raise ValueError('robots.txt requires a User-agent: * group')
        if release:
            if ('allow', '/') not in wildcard or any(key == 'disallow' and value in ('/', '/*') for key, value in wildcard):
                raise ValueError('release wildcard group must allow the public site')
            for path in paths:
                public_path = page_path(path.relative_to(root))
                matching = []
                for key, value in wildcard:
                    if value:
                        pattern = re.escape(value.rstrip('$')).replace(r'\*', '.*')
                        if re.match(pattern + ('$' if value.endswith('$') else ''), public_path):
                            matching.append((len(value), key == 'allow'))
                if matching and not max(matching)[1]:
                    raise ValueError(f'public file is blocked by wildcard rules: {public_path}')
            if domain and sitemaps != [domain + '/sitemap.xml']:
                raise ValueError('release robots.txt must reference the canonical sitemap')
        elif ('disallow', '/') not in wildcard or sitemaps:
            raise ValueError('draft robots.txt must disallow / and omit sitemap publication')
    except (OSError, UnicodeError, ValueError) as exc:
        fail('indexing', f'robots.txt: {exc}.')
    return report()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site_dir')
    parser.add_argument('--release', action='store_true')
    parser.add_argument('--domain', help='Full public HTTPS origin, e.g. https://example.com')
    args = parser.parse_args()
    result = audit_site(args.site_dir, args.release, args.domain)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
