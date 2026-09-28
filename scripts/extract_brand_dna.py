#!/usr/bin/env python3
"""Create suggested brand colors and CSS; does not certify site accessibility."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from design_math import contrast, fluid_css

NEUTRAL = '#334155'


def hex_to_rgb(value):
    if not isinstance(value, str) or not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', value):
        raise ValueError('Color must be #RGB or #RRGGBB hexadecimal notation')
    value = value[1:]
    if len(value) == 3:
        value = ''.join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    if any(type(v) is not int or not 0 <= v <= 255 for v in (r, g, b)):
        raise ValueError('RGB channels must be integers between 0 and 255')
    return f'#{r:02X}{g:02X}{b:02X}'


def contrast_ratio(rgb1, rgb2):
    return contrast(rgb_to_hex(*rgb1), rgb_to_hex(*rgb2))


def _text_color(background):
    bg = hex_to_rgb(background)
    color = max(('#000000', '#FFFFFF'), key=lambda c: contrast_ratio(bg, hex_to_rgb(c)))
    ratio = contrast_ratio(bg, hex_to_rgb(color))
    if ratio < 4.5:
        raise ValueError('No accessible text color for supplied background')
    return color, ratio


def generate_tokens(primary, accent, brand_name):
    primary = rgb_to_hex(*hex_to_rgb(primary))
    accent = rgb_to_hex(*hex_to_rgb(accent))
    primary_text, primary_ratio = _text_color(primary)
    accent_text, accent_ratio = _text_color(accent)
    return {
        'brand_name': str(brand_name),
        'color_source': 'supplied_color',
        'color_note': 'Suggested palette; confirm brand usage before publication.',
        'colors': {
            'primary': primary, 'primary_rgb': ', '.join(map(str, hex_to_rgb(primary))),
            'accent': accent, 'accent_rgb': ', '.join(map(str, hex_to_rgb(accent))),
            'surface_bg': '#F8FAFC', 'surface_card': '#FFFFFF', 'border': '#CBD5E1',
            'text_primary': '#0F172A', 'text_secondary': '#475569', 'text_muted': '#475569',
            'text_on_primary': primary_text, 'text_on_accent': accent_text,
        },
        'typography': {
            'font_display': "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'font_body': "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            'font_mono': "ui-monospace, 'SFMono-Regular', Consolas, monospace",
        },
        'contrast_checks': {
            'scope': 'Opaque primary/accent button background and chosen black/white text only',
            'minimum_ratio': 4.5,
            'primary_text_ratio': round(primary_ratio, 3),
            'accent_text_ratio': round(accent_ratio, 3),
            'status': 'PASS',
            'site_wcag_status': 'NOT_TESTED',
        },
    }


def _sample_logo(logo_path):
    if not logo_path:
        return NEUTRAL, 'neutral_fallback', 'No logo supplied; neutral starter color selected.'
    path = Path(logo_path)
    if not path.is_file():
        return NEUTRAL, 'neutral_fallback', 'Logo file missing or not a regular file; neutral starter color selected.'
    if path.suffix.lower() == '.svg':
        return NEUTRAL, 'neutral_fallback', 'SVG is not rasterized by this tool; supply a reviewed color or raster logo.'
    try:
        from PIL import Image
    except ImportError:
        return NEUTRAL, 'neutral_fallback', 'Optional Pillow is unavailable; supply --primary or install Pillow for raster sampling.'
    try:
        with Image.open(path) as source:
            source.thumbnail((128, 128))
            rgba = source.convert('RGBA')
            # ponytail: quantized dominant pixel sampling is a proposal; use reviewed colors for complex logos.
            counts = Counter((r // 16 * 16, g // 16 * 16, b // 16 * 16)
                             for r, g, b, a in rgba.getdata()
                             if a >= 128 and min(r, g, b) < 245)
        if not counts:
            return NEUTRAL, 'neutral_fallback', 'Logo has no usable opaque nonwhite sample; neutral starter color selected.'
        return rgb_to_hex(*counts.most_common(1)[0][0]), 'raster_sample', 'Dominant quantized raster color sampled; confirm with the brand owner.'
    except (OSError, ValueError, Image.DecompressionBombError):
        return NEUTRAL, 'neutral_fallback', 'Raster logo could not be decoded safely; neutral starter color selected.'


def build_tokens(logo_path: str | None, brand_name: str, primary: str | None = None) -> dict:
    if primary is not None:
        color = rgb_to_hex(*hex_to_rgb(primary))
        source, note = 'supplied_color', 'Explicit color supplied; the same color is used for action accents.'
    else:
        color, source, note = _sample_logo(logo_path)
    tokens = generate_tokens(color, color, brand_name)
    tokens.update(color_source=source, color_note=note)
    return tokens


def extract_colors_from_image(image_path):
    """Compatibility helper. Use build_tokens() to retain source and fallback status."""
    color, _, _ = _sample_logo(image_path)
    return color, color


def write_tokens_css(tokens, path, language='en', layout='engineering'):
    colors = tokens['colors']
    # Validate every color again at the CSS boundary; do not interpolate brand names or freeform typography.
    for key in ('primary', 'accent', 'surface_bg', 'surface_card', 'border', 'text_primary',
                'text_secondary', 'text_muted', 'text_on_primary', 'text_on_accent'):
        hex_to_rgb(colors[key])
    names = {
        'brand-primary': 'primary', 'brand-accent': 'accent', 'brand-surface': 'surface_bg',
        'brand-surface-card': 'surface_card', 'brand-border': 'border',
        'text-primary': 'text_primary', 'text-secondary': 'text_secondary', 'text-muted': 'text_muted',
        'text-on-primary': 'text_on_primary', 'text-on-accent': 'text_on_accent',
    }
    lines = ['/* Suggested CSS variables; site accessibility requires separate verification. */', ':root {']
    lines += [f'  --{name}: {rgb_to_hex(*hex_to_rgb(colors[key]))};' for name, key in names.items()]
    lines += [f"  --brand-{name}-rgb: {', '.join(map(str, hex_to_rgb(colors[name])))};" for name in ('primary', 'accent')]
    language = language.lower()
    fallback = 'system-ui, -apple-system, "Segoe UI", sans-serif'
    if language.startswith(('zh-hant', 'zh-tw', 'zh-hk')):
        fallback = 'system-ui, "PingFang TC", "Noto Sans CJK TC", "Microsoft JhengHei", sans-serif'
    elif language.startswith('zh'):
        fallback = 'system-ui, "PingFang SC", "Noto Sans CJK SC", "Microsoft YaHei", sans-serif'
    elif language.startswith('ja'):
        fallback = 'system-ui, "Hiragino Kaku Gothic ProN", "Noto Sans CJK JP", "Yu Gothic", sans-serif'
    elif language.startswith('ko'):
        fallback = 'system-ui, "Apple SD Gothic Neo", "Noto Sans CJK KR", "Malgun Gothic", sans-serif'
    display = 'Georgia, "Times New Roman", serif' if layout == 'materials' and language.split('-')[0] in ('en','de','fr','es','it','pt') else fallback
    tokens['typography'].update(font_display=display, font_body=fallback,
        display_size=fluid_css(36,64,360,1440,16), section_size=fluid_css(26,36,360,1440,16),
        root_assumption_px=16, font_loading='System/local fallbacks only; no font downloads')
    lines += [
        f'  --font-display: {display};',
        f'  --font-body: {fallback};',
        '  --font-mono: ui-monospace, monospace;',
        f'  --text-display: {tokens["typography"]["display_size"]};',
        f'  --text-section: {tokens["typography"]["section_size"]};',
        '  --text-small: .875rem; --text-body: 1rem;',
        '  --space-1: .5rem; --space-2: 1rem; --space-3: 1.5rem; --space-4: 2rem;',
        '  --section-space: clamp(2.5rem, 5vw, 5rem);',
        '  --content-width: 75rem; --reading-width: 65ch;',
        '  --focus-color: #0F172A; --control-border: #64748B;',
        '  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 10px; --radius-full: 9999px;',
        '  --shadow-bento: 0 1px 3px rgba(0,0,0,.05), 0 0 0 1px var(--brand-border);',
        '  --shadow-hover: 0 10px 25px -5px rgba(0,0,0,.08), 0 0 0 1px var(--brand-border);',
        '}', '',
    ]
    Path(path).write_text('\n'.join(lines), encoding='utf-8')


def self_test():
    for color in ('#fff', '#000', '#777777', '#767676', '#FFFF00', '#000080', '#FF6B35'):
        tokens = build_tokens(None, 'Test', primary=color)
        for name in ('primary', 'accent'):
            assert contrast_ratio(hex_to_rgb(tokens['colors'][name]), hex_to_rgb(tokens['colors']['text_on_' + name])) >= 4.5
        assert tokens['color_source'] == 'supplied_color'
    for bad in ('red', '123456', '#12', '#abcd', '#1234567', '#123456; color:red', '', None, 123):
        try:
            generate_tokens(bad, '#fff', 'Test')
        except ValueError:
            pass
        else:
            raise AssertionError(f'Invalid color accepted: {bad!r}')
    assert build_tokens(None, 'Test')['color_source'] == 'neutral_fallback'
    assert build_tokens('/definitely-not-a-logo', 'Test')['color_source'] == 'neutral_fallback'
    print('PASS: color validation, dark/light/midpoint button contrast, explicit fallback')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logo_path', nargs='?')
    parser.add_argument('brand_name', nargs='?')
    parser.add_argument('output_dir', nargs='?')
    parser.add_argument('--primary')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.brand_name or not args.output_dir:
        parser.error('logo_path, brand_name, output_dir are required unless --self-test is supplied')
    tokens = build_tokens(args.logo_path, args.brand_name, args.primary)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_tokens_css(tokens, out / 'tokens.css')
    (out / 'brand_tokens.json').write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Brand palette: {tokens['color_source']}. {tokens['color_note']}")


if __name__ == '__main__':
    main()
