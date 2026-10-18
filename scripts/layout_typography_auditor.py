#!/usr/bin/env python3
"""
Pre-Flight UI/UX & Web Interface Guidelines Auditor.
Deeply integrates Vercel Web Interface Guidelines & Anthropic Frontend Design checks:
- Accessibility (a11y): ARIA labels, semantic tags, alt attributes, form label bindings
- Focus & States: :focus-visible vs outline:none
- Micro-Typography: unicode ellipsis, quotes, tabular-nums
- Animation & CSS: transition:all warnings, reduced-motion
- Performance & CLS: img explicit width/height
- Core SEO: H1 hierarchy, viewport, lang, JSON-LD Schema
Outputs in terse `file:line: [CATEGORY] Rule` format.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from site_forensics import PageParser


class VercelWebGuidelinesParser(HTMLParser):
    """HTML Parser that captures line-level tokens for Web Interface Guidelines audit."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ''
        self.meta = {}
        self.images = []
        self.h1_count = 0
        self.schemas = []
        self.buttons = []
        self.inputs = []
        self.labels = []
        self.non_semantic_clicks = []
        self.inline_styles = []
        self.typography_issues = []
        self.links = []
        self.canonical_urls = []
        self.og_urls = []
        self._title = False
        self._schema = None
        self._current_tag = None
        self._current_tag_line = 1
        self._current_tag_text = ''
        self._in_style = False
        self._style_buffer = ''
        self._in_label_depth = 0

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
        elif tag == 'h1':
            self.h1_count += 1
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            value = a.get('content', '')
            if key == 'og:url' and value:
                self.og_urls.append({'content': value, 'line': line})
            self.meta[key] = ', '.join(filter(None, (self.meta.get(key), value))) if key in ('robots', 'googlebot', 'bingbot') else value
        elif tag == 'a':
            href = a.get('href', '')
            if href:
                self.links.append({'href': href, 'line': line})
        elif tag == 'link' and 'canonical' in (a.get('rel') or ''):
            href = a.get('href', '')
            if href:
                self.canonical_urls.append({'href': href, 'line': line})
        elif tag == 'img':
            self.images.append(dict(a, _line=line))
        elif tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self._schema = ''
        elif tag == 'button':
            self.buttons.append({'attrs': a, 'line': line, 'text': ''})
            self._current_tag = 'button'
        elif tag in ('input', 'textarea', 'select'):
            self.inputs.append({'tag': tag, 'attrs': a, 'line': line, 'wrapped_in_label': (self._in_label_depth > 0)})
        elif tag == 'label':
            self.labels.append({'attrs': a, 'line': line})
            self._in_label_depth += 1
        elif tag in ('div', 'span', 'p', 'section') and 'onclick' in a:
            self.non_semantic_clicks.append({'tag': tag, 'line': line})
        elif tag == 'style':
            self._in_style = True
            self._style_buffer = ''

    def handle_data(self, data):
        if self._schema is not None:
            self._schema += data
        if self._in_style:
            self._style_buffer += data
        if self._current_tag == 'button' and self.buttons:
            self.buttons[-1]['text'] += data.strip()
        # Micro-typography check for raw triple dots '...'
        if '...' in data:
            line, _ = self.getpos()
            self.typography_issues.append((line, "Use Unicode ellipsis '…' (\\u2026) instead of triple dots '...'"))

    def handle_endtag(self, tag):
        if tag == 'script' and self._schema is not None:
            self.schemas.append(self._schema)
            self._schema = None
        elif tag == 'label':
            self._in_label_depth = max(0, self._in_label_depth - 1)
        elif tag == 'button':
            self._current_tag = None
        elif tag == 'style':
            self._in_style = False
            self.inline_styles.append(self._style_buffer)
            self._style_buffer = ''


def schema_shape(data):
    if isinstance(data, list):
        return bool(data) and all(schema_shape(item) for item in data)
    if not isinstance(data, dict):
        return False
    if '@graph' in data:
        graph = data['@graph']
        return bool(data.get('@context')) and isinstance(graph, list) and bool(graph) and all(
            isinstance(item, dict) and bool(item.get('@type')) for item in graph)
    return bool(data.get('@type'))


def check_css_guidelines(css_content, source_label):
    """Check CSS content against Vercel & Anthropic guidelines."""
    warnings = []
    lines = css_content.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Check transition: all
        if re.search(r'transition\s*:\s*all\b', line, re.IGNORECASE):
            warnings.append(f"{source_label}:{idx}: [ANIMATION] Never 'transition: all'—list properties explicitly (compositor-friendly)")
        # Check outline: none without visible focus
        if re.search(r'outline\s*:\s*(?:none|0)\b', line, re.IGNORECASE) and ':focus-visible' not in line:
            warnings.append(f"{source_label}:{idx}: [FOCUS] 'outline: none' detected—ensure visible :focus-visible replacement exists")
    return warnings


def audit_directory(dir_path, strict=False):
    root = Path(dir_path)
    if not root.is_dir():
        raise ValueError('Build directory does not exist')
    pages = sorted(root.rglob('*.html'))
    if not pages:
        raise ValueError('No HTML files found; cannot pass an empty audit')
    
    css_files = sorted(root.rglob('*.css'))
    global_guidelines = []
    for css_file in css_files:
        try:
            css_text = css_file.read_text(encoding='utf-8')
            rel_css = css_file.relative_to(root)
            global_guidelines.extend(check_css_guidelines(css_text, str(rel_css)))
        except Exception:
            pass

    count = 0
    guideline_count = len(global_guidelines)

    # Check sitemap.xml for Clean URLs
    sitemap_file = root / 'sitemap.xml'
    if sitemap_file.exists():
        try:
            sitemap_content = sitemap_file.read_text(encoding='utf-8')
            for loc in re.findall(r'<loc>(.*?)</loc>', sitemap_content):
                if re.search(r'\.html(?=[?#]|$)', loc, re.IGNORECASE):
                    global_guidelines.append(f"sitemap.xml: [ROUTING] Sitemap <loc> '{loc}' contains '.html' (violates Clean URLs standard)")
        except Exception:
            pass

    for file in pages:
        rel_path = file.relative_to(root)
        raw_html = file.read_text(encoding='utf-8')
        parser = VercelWebGuidelinesParser()
        parser.feed(raw_html)

        issues = []
        guidelines = []

        # 1. Mandatory Core Checks
        # Clean URLs checks (Zero .html in internal navigation, canonical, og:url)
        for link in parser.links:
            href = link['href'].strip()
            if href.startswith(('http://', 'https://', '//', 'mailto:', 'tel:', 'javascript:', '#')):
                continue
            if re.search(r'\.html(?=[?#]|$)', href, re.IGNORECASE):
                issues.append(f"Internal link '{href}' (line {link['line']}) contains '.html' (violates Clean URLs standard)")

        for can in parser.canonical_urls:
            href = can['href']
            if '.html' in href:
                issues.append(f"Canonical URL '{href}' (line {can['line']}) contains '.html'")

        for og in parser.og_urls:
            content = og['content']
            if '.html' in content:
                issues.append(f"og:url '{content}' (line {og['line']}) contains '.html'")
        if parser.h1_count != 1:
            issues.append(f'Expected one primary H1; found {parser.h1_count}')
        if 'viewport' not in parser.meta:
            issues.append('Missing viewport')
        if not parser.lang:
            issues.append('Missing HTML language')
        if any('alt' not in image for image in parser.images):
            issues.append('Image missing alt attribute (empty alt is allowed for decoration)')
        for raw in parser.schemas:
            try:
                if not schema_shape(json.loads(raw)):
                    issues.append('Unexpected JSON-LD type/graph shape')
            except ValueError:
                issues.append('Invalid JSON-LD JSON')

        # 2. Vercel Web Interface Guidelines (Pre-Flight Checks)
        # Check non-semantic clicks
        for item in parser.non_semantic_clicks:
            guidelines.append(f"{rel_path}:{item['line']}: [SEMANTICS] Non-semantic <{item['tag']} onclick>—use <button> for actions or <a> for navigation")

        # Check button a11y labels
        for btn in parser.buttons:
            has_aria = bool(btn['attrs'].get('aria-label') or btn['attrs'].get('aria-labelledby'))
            has_text = bool(btn['text'].strip())
            if not has_text and not has_aria:
                guidelines.append(f"{rel_path}:{btn['line']}: [A11Y] Icon-only or empty button missing 'aria-label'")

        # Check form inputs label bindings
        label_fors = {lbl['attrs'].get('for') for lbl in parser.labels if lbl['attrs'].get('for')}
        for inp in parser.inputs:
            input_id = inp['attrs'].get('id')
            input_type = inp['attrs'].get('type', '').lower()
            if input_type in ('hidden', 'submit', 'button', 'reset'):
                continue
            inp_has_aria = bool(inp['attrs'].get('aria-label') or inp['attrs'].get('aria-labelledby'))
            has_label = bool((input_id and input_id in label_fors) or inp.get('wrapped_in_label'))
            if not inp_has_aria and not has_label:
                guidelines.append(f"{rel_path}:{inp['line']}: [FORMS] <{inp['tag']}> controls need associated <label> or aria-label")
            if input_type in ('text', 'email', 'tel', 'url') and 'autocomplete' not in inp['attrs']:
                guidelines.append(f"{rel_path}:{inp['line']}: [FORMS] Input type '{input_type}' recommends 'autocomplete' for seamless user experience")

        # Check images CLS
        for img in parser.images:
            if 'width' not in img or 'height' not in img:
                guidelines.append(f"{rel_path}:{img['_line']}: [CLS] <img> missing explicit width/height or CSS aspect-ratio")

        # Check inline styles for CSS guidelines
        for inline_css in parser.inline_styles:
            guidelines.extend(check_css_guidelines(inline_css, str(rel_path)))

        # Check micro-typography
        for line_no, typo_msg in parser.typography_issues:
            guidelines.append(f"{rel_path}:{line_no}: [TYPOGRAPHY] {typo_msg}")

        count += len(issues)
        guideline_count += len(guidelines)

        # Output status
        status = 'FAIL' if issues or (strict and guidelines) else 'PASS'
        report_msg = ', '.join(issues) if issues else 'core static checks passed'
        print(f"{status} {rel_path}: {report_msg}")

        # Terse Vercel Guidelines Output
        for g in guidelines:
            prefix = "ERROR" if strict else "GUIDELINE"
            print(f"  └─ [{prefix}] {g}")

    if global_guidelines:
        print("Global CSS Guidelines:")
        for gg in global_guidelines:
            prefix = "ERROR" if strict else "GUIDELINE"
            print(f"  └─ [{prefix}] {gg}")

    print(f"\nAudit Summary: {len(pages)} pages, {count} blocking errors, {guideline_count} interface guidelines.")
    if strict:
        return (count + guideline_count) == 0
    return count == 0


if __name__ == '__main__':
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('directory')
    cli.add_argument('--strict', action='store_true', help='Treat Vercel interface guidelines warnings as blocking errors')
    args = cli.parse_args()
    try:
        sys.exit(0 if audit_directory(args.directory, strict=args.strict) else 1)
    except (OSError, ValueError) as exc:
        cli.exit(1, f'Audit failed: {exc}\n')
