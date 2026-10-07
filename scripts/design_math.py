#!/usr/bin/env python3
"""
B2B Global Brand Site Master
Design Math, Fluid Typography & Container Loading Estimator
Python standard library only.
"""
import argparse
import json
import math
import re


# ---------------------------------------------------------------------------
# 1. WCAG Color Contrast Calculation
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 2. Fluid Typography & Spacing Clamp Calculator
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 3. B2B Packaging & Container Loading Estimator (20GP / 40GP / 40HQ)
# ---------------------------------------------------------------------------
CONTAINERS = {
    "20GP": {"cbm": 33.1, "max_payload_kg": 21800, "name": "20' General Purpose Container"},
    "40GP": {"cbm": 67.5, "max_payload_kg": 26680, "name": "40' General Purpose Container"},
    "40HQ": {"cbm": 76.2, "max_payload_kg": 26580, "name": "40' High Cube Container"},
}


def estimate_container(length_mm, width_mm, height_mm, gross_weight_kg, pcs_per_carton, efficiency=0.88):
    if any(v <= 0 for v in (length_mm, width_mm, height_mm, gross_weight_kg, pcs_per_carton)):
        raise ValueError("Carton dimensions, weight, and pcs per carton must be positive numbers.")
    if not (0 < efficiency <= 1.0):
        raise ValueError("Efficiency factor must be between 0 and 1.0.")
    
    cbm_per_carton = (length_mm * width_mm * height_mm) / 1_000_000_000.0
    
    summary = {
        "carton_specs": {
            "dimensions_mm": f"{length_mm} x {width_mm} x {height_mm}",
            "cbm_per_carton": round(cbm_per_carton, 4),
            "gross_weight_kg": gross_weight_kg,
            "pcs_per_carton": pcs_per_carton,
            "packing_efficiency_factor": efficiency
        },
        "container_estimates": {}
    }

    for c_id, spec in CONTAINERS.items():
        usable_cbm = spec["cbm"] * efficiency
        by_volume = math.floor(usable_cbm / cbm_per_carton)
        by_weight = math.floor(spec["max_payload_kg"] / gross_weight_kg)
        max_cartons = min(by_volume, by_weight)
        limiting_factor = "Volume" if by_volume <= by_weight else "Weight"
        total_units = max_cartons * pcs_per_carton
        total_weight = round(max_cartons * gross_weight_kg, 1)
        total_cbm = round(max_cartons * cbm_per_carton, 2)
        utilization = round((total_cbm / spec["cbm"]) * 100, 1)

        summary["container_estimates"][c_id] = {
            "container_name": spec["name"],
            "max_cartons": max_cartons,
            "total_units": total_units,
            "total_cbm": total_cbm,
            "total_gross_weight_kg": total_weight,
            "volumetric_utilization_pct": utilization,
            "limiting_factor": limiting_factor
        }

    return summary


# ---------------------------------------------------------------------------
# 4. Self Test Suite
# ---------------------------------------------------------------------------
def self_test():
    # Contrast tests
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

    # Fluid typography tests
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

    # Container estimator test (Standard Bentgo Kids 5-Comp Bento Box carton: 540x380x420mm, 24 pcs, 14.5kg)
    est = estimate_container(540, 380, 420, 14.5, 24)
    assert "40HQ" in est["container_estimates"]
    hq = est["container_estimates"]["40HQ"]
    assert hq["total_units"] >= 18000
    assert hq["limiting_factor"] == "Volume"

    # Reject invalid container parameters
    for bad_args in (
        (-10, 380, 420, 14.5, 24),
        (540, 0, 420, 14.5, 24),
        (540, 380, -5, 14.5, 24),
        (540, 380, 420, 0, 24),
        (540, 380, 420, 14.5, 0),
    ):
        try:
            estimate_container(*bad_args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Accepted invalid container args: {bad_args}")

    print("PASS: contrast reference values, fluid interpolation, and container logistics math")


# ---------------------------------------------------------------------------
# 5. CLI Controller
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    # Contrast command
    colors = commands.add_parser("contrast", help="Opaque sRGB text contrast; failure exits 1")
    colors.add_argument("foreground")
    colors.add_argument("background")
    colors.add_argument("--large", action="store_true", help="Use 3:1 for qualifying large text")

    # Fluid clamp command
    fluid = commands.add_parser("fluid", help="Sizes/widths in CSS px; root is 16px by default")
    for name in ("min_size", "max_size", "min_width", "max_width"):
        fluid.add_argument(name, type=float)
    fluid.add_argument("--root", type=float, default=16)

    # Container loading estimator command
    box = commands.add_parser("container", help="Calculate 20GP/40GP/40HQ container loading capacity for export")
    box.add_argument("--length", type=float, required=True, help="Carton length in mm")
    box.add_argument("--width", type=float, required=True, help="Carton width in mm")
    box.add_argument("--height", type=float, required=True, help="Carton height in mm")
    box.add_argument("--weight", type=float, required=True, help="Carton gross weight in kg")
    box.add_argument("--pcs", type=int, required=True, help="Pieces per master carton")
    box.add_argument("--efficiency", type=float, default=0.88, help="Packing efficiency factor (default 0.88)")

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

        if args.command == "container":
            result = estimate_container(args.length, args.width, args.height, args.weight, args.pcs, args.efficiency)
            print(json.dumps(result, indent=2))
            return 0

        self_test()
        return 0
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
