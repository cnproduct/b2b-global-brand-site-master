#!/usr/bin/env python3
"""Opaque sRGB contrast and fluid type interpolation; Python standard library only."""
import argparse
import math
import re


def luminance(color):
    if not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", color):
        raise ValueError("Use opaque #RGB or #RRGGBB; composite transparency separately.")
    value = color[1:]
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def fluid_coefficients(min_size, max_size, min_width, max_width, root):
    values = (min_size, max_size, min_width, max_width, root)
    if not all(math.isfinite(v) and v > 0 for v in values):
        raise ValueError("Sizes, widths and root must be positive finite numbers.")
    if max_width <= min_width or max_size < min_size:
        raise ValueError("Require max_width > min_width and max_size >= min_size.")
    slope = (max_size - min_size) / (max_width - min_width)
    intercept = min_size - slope * min_width
    result = (min_size / root, intercept / root, slope * 100, max_size / root)
    if not all(math.isfinite(v) for v in result):
        raise ValueError("Values are too extreme for finite CSS coefficients.")
    return result


def fluid_css(*values):
    low, intercept, vw, high = fluid_coefficients(*values)
    return f"clamp({low:.10g}rem, calc({intercept:.10g}rem + {vw:.10g}vw), {high:.10g}rem)"


def self_test():
    assert math.isclose(contrast("#000", "#fff"), 21)
    assert math.isclose(contrast("#abc", "#aabbcc"), 1)
    assert math.isclose(contrast("#fff", "#000"), contrast("#000", "#fff"))
    assert contrast("#767676", "#fff") >= 4.5
    assert contrast("#777777", "#fff") < 4.5
    assert math.isclose(luminance("#ff0000"), 0.2126)
    for invalid in ("red", "#abcd", "#ffffff00", "#ggg", "fff", "#12"):
        try:
            contrast(invalid, "#fff")
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted invalid color {invalid}")
    for sizes in ((16, 20, 360, 1280, 16), (24, 64, 320, 1440, 16),
                  (18, 18, 320, 1280, 20)):
        low, intercept, vw, high = fluid_coefficients(*sizes)
        for width, expected in ((sizes[2], sizes[0]), (sizes[3], sizes[1]),
                                ((sizes[2] + sizes[3]) / 2, (sizes[0] + sizes[1]) / 2)):
            actual = min(high * sizes[4], max(low * sizes[4],
                         intercept * sizes[4] + vw * width / 100))
            assert math.isclose(actual, expected, abs_tol=1e-9)
        css = fluid_css(*sizes)
        match = re.fullmatch(r"clamp\(([-\de.+]+)rem, calc\(([-\de.+]+)rem \+ ([-\de.+]+)vw\), ([-\de.+]+)rem\)", css)
        assert match, css
        emitted = tuple(map(float, match.groups()))
        assert all(math.isclose(a, b, abs_tol=1e-8) for a, b in zip(emitted, (low, intercept, vw, high)))
    for values in ((16, 20, 360, 360, 16), (20, 16, 360, 1280, 16),
                   (0, 20, 360, 1280, 16), (16, 20, 360, 1280, 0),
                   (16, float("nan"), 360, 1280, 16),
                   (16, float("inf"), 360, 1280, 16)):
        try:
            fluid_coefficients(*values)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted invalid dimensions {values}")
    print("PASS: contrast reference values, thresholds, input rejection and fluid endpoints/output")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    colors = commands.add_parser("contrast", help="Opaque sRGB text contrast; failure exits 1")
    colors.add_argument("foreground")
    colors.add_argument("background")
    colors.add_argument("--large", action="store_true", help="Use 3:1 for qualifying large text")
    fluid = commands.add_parser("fluid", help="Sizes/widths in CSS px; root is a design assumption")
    for name in ("min_size", "max_size", "min_width", "max_width"):
        fluid.add_argument(name, type=float)
    fluid.add_argument("--root", type=float, default=16)
    commands.add_parser("self-test")
    args = parser.parse_args()
    try:
        if args.command == "contrast":
            ratio = contrast(args.foreground, args.background)
            threshold = 3 if args.large else 4.5
            passed = ratio >= threshold
            print(f"{ratio:.6f}:1 — {'PASS' if passed else 'FAIL'} (AA text threshold {threshold}:1)")
            print("Decision uses the unrounded ratio; opaque colors only, not a full page audit.")
            return 0 if passed else 1
        if args.command == "fluid":
            print(fluid_css(args.min_size, args.max_size, args.min_width, args.max_width, args.root))
            return 0
        self_test()
        return 0
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
