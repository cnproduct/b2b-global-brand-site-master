#!/usr/bin/env python3
"""
B2B Global Brand Site Master
Design Math, Fluid Typography, Defensive URL Normalization & Dual-Mode Container Loading Estimator
(Volumetric Carton Mode + Heavy-Cargo Stone/Building Material Mode)
Python standard library only.
"""
import argparse
import json
import math
import re
import urllib.parse


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
# 3. Defensive URL Path Normalization & Verification (Guardrail 1)
# ---------------------------------------------------------------------------
def safe_urljoin(domain: str, path: str) -> str:
    """
    Safely joins a domain and a path, strictly preventing missing slash
    glitches (e.g. 'domain.compath') and duplicate slashes.
    """
    if not domain:
        raise ValueError("Domain cannot be empty.")
    domain_clean = domain.rstrip("/")
    path_clean = path.lstrip("/") if path else ""
    joined = f"{domain_clean}/{path_clean}" if path_clean else f"{domain_clean}/"
    if not is_valid_url(joined):
        raise ValueError(f"Malformed URL generated: {joined}")
    return joined


def is_valid_url(url: str) -> bool:
    """
    Checks if a URL has valid scheme, host, and proper path separation.
    Rejects malformed concatenations like 'https://tianyalimestone.comstone-flooring'.
    """
    if not url or not isinstance(url, str):
        return False
    parsed = urllib.parse.urlparse(url)
    if not (parsed.scheme in ("http", "https") and parsed.netloc):
        return False
    parts = parsed.netloc.split(".")
    if len(parts) < 2:
        return False
    last = parts[-1].lower()
    if re.match(r"^(com|org|net|io|edu|gov|cn|uk|de|au|ru|kz|uz)[a-zA-Z0-9_-]+", last):
        return False
    return True


# ---------------------------------------------------------------------------
# 4A. Volumetric / Standard Carton Container Loading Estimator (20GP / 40GP / 40HQ)
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
        "mode": "volumetric_carton",
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
# 4B. Heavy Cargo Natural Stone & Building Materials 20GP Estimator (Guardrail 3)
# ---------------------------------------------------------------------------
CONTAINER_20GP_HEAVY = {
    "name": "20' Heavy-Duty General Purpose Container",
    "max_cargo_payload_kg": 26500,  # Typical port/rail allowable stone payload (e.g., Xiamen Port / Eurasian Rail)
    "cbm_volume": 33.1,
    "max_crates": 24,               # Maximum standard ISPM 15 wooden crates floor plan (12 stacks x 2)
}


def estimate_stone_container(area_m2, thickness_mm=20.0, density_kg_m3=2620.0, crate_capacity_m2=None, max_payload_kg=26500.0):
    """
    Calculates 20GP container loading, crate count, and weight for heavy cargo
    such as natural limestone, marble, granite, sintered stone, or heavy slabs.
    For high-density limestone (2,620 kg/m³):
    - 20mm thickness ~= 52.4 kg/m² -> ~480-504 m² per 20GP
    - 30mm thickness ~= 78.6 kg/m² -> ~320-336 m² per 20GP
    """
    if any(v <= 0 for v in (area_m2, thickness_mm, density_kg_m3, max_payload_kg)):
        raise ValueError("Area, thickness, density, and max payload must be positive numbers.")

    thickness_m = thickness_mm / 1000.0
    weight_per_m2 = density_kg_m3 * thickness_m
    total_net_stone_weight_kg = area_m2 * weight_per_m2
    total_volume_m3 = area_m2 * thickness_m

    if crate_capacity_m2 is None:
        crate_capacity_m2 = 24.0 if thickness_mm <= 22 else 16.0
    if crate_capacity_m2 <= 0:
        raise ValueError("Crate capacity must be positive.")

    total_crates = math.ceil(area_m2 / crate_capacity_m2)
    tare_weight_per_crate_kg = 50.0  # ISPM 15 fumigated reinforced timber crate tare
    total_gross_weight_kg = total_net_stone_weight_kg + (total_crates * tare_weight_per_crate_kg)

    by_weight_containers = math.ceil(total_gross_weight_kg / max_payload_kg)
    by_crate_containers = math.ceil(total_crates / CONTAINER_20GP_HEAVY["max_crates"])
    required_20gp_containers = max(by_weight_containers, by_crate_containers)

    limiting_factor = "Weight (Heavy Cargo Limit)" if by_weight_containers >= by_crate_containers else "Floor Crate Layout"
    max_m2_per_container = math.floor(max_payload_kg / (weight_per_m2 + (tare_weight_per_crate_kg / crate_capacity_m2)))

    return {
        "mode": "deadweight_heavy_cargo",
        "input_specification": {
            "requested_area_m2": round(area_m2, 2),
            "thickness_mm": thickness_mm,
            "density_kg_m3": density_kg_m3,
            "unit_weight_kg_m2": round(weight_per_m2, 2)
        },
        "packaging_summary": {
            "total_crates": total_crates,
            "m2_per_crate": crate_capacity_m2,
            "total_net_weight_kg": round(total_net_stone_weight_kg, 1),
            "total_gross_weight_kg": round(total_gross_weight_kg, 1),
            "total_volume_m3": round(total_volume_m3, 3)
        },
        "shipping_estimates": {
            "required_20gp_containers": required_20gp_containers,
            "limiting_factor": limiting_factor,
            "weight_utilization_pct": round((total_gross_weight_kg / (required_20gp_containers * max_payload_kg)) * 100, 1),
            "max_safe_m2_per_single_20gp": max_m2_per_container,
            "max_payload_kg": max_payload_kg
        }
    }


# ---------------------------------------------------------------------------
# 5. Self Test Suite
# ---------------------------------------------------------------------------
def self_test():
    # Contrast tests
    assert math.isclose(contrast("#000", "#fff"), 21)
    assert math.isclose(contrast("#abc", "#aabbcc"), 1)
    assert math.isclose(contrast("#fff", "#000"), contrast("#000", "#fff"))
    assert contrast("#767676", "#fff") >= 4.5
    assert contrast("#777777", "#fff") < 4.5
    assert contrast("#251700", "#ffffff") >= 17.0
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
                  (18, 18, 320, 1280, 20), (36, 60, 360, 1440, 16)):
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

    # Defensive URL Normalization (Guardrail 1)
    u1 = safe_urljoin("https://tianyalimestone.com", "stone-flooring/limestone/antique/lanting")
    assert u1 == "https://tianyalimestone.com/stone-flooring/limestone/antique/lanting"
    assert is_valid_url(u1)
    assert not is_valid_url("https://tianyalimestone.comstone-flooring/limestone")
    assert not is_valid_url("invalid-url")

    # Volumetric container estimator test (Bento Box carton: 540x380x420mm, 24 pcs, 14.5kg)
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

    # Heavy cargo stone container estimation (Guardrail 3)
    est_20mm = estimate_stone_container(480, 20)
    assert est_20mm["shipping_estimates"]["required_20gp_containers"] == 1
    assert est_20mm["shipping_estimates"]["limiting_factor"] == "Weight (Heavy Cargo Limit)"
    assert est_20mm["shipping_estimates"]["max_safe_m2_per_single_20gp"] <= 510

    est_30mm = estimate_stone_container(1000, 30)
    assert est_30mm["shipping_estimates"]["required_20gp_containers"] >= 3

    print("PASS: contrast reference values, fluid interpolation, safe URL join, and dual-mode container logistics math")


# ---------------------------------------------------------------------------
# 6. CLI Controller
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

    # Safe urljoin command
    url_cmd = commands.add_parser("safe-url", help="Safely join domain and path with slash defense")
    url_cmd.add_argument("domain", help="Base domain e.g. https://tianyalimestone.com")
    url_cmd.add_argument("path", help="Relative path e.g. stone-flooring/limestone")

    # Volumetric container loading estimator command
    box = commands.add_parser("container", help="Calculate 20GP/40GP/40HQ container loading capacity for carton goods")
    box.add_argument("--length", type=float, required=True, help="Carton length in mm")
    box.add_argument("--width", type=float, required=True, help="Carton width in mm")
    box.add_argument("--height", type=float, required=True, help="Carton height in mm")
    box.add_argument("--weight", type=float, required=True, help="Carton gross weight in kg")
    box.add_argument("--pcs", type=int, required=True, help="Pieces per master carton")
    box.add_argument("--efficiency", type=float, default=0.88, help="Packing efficiency factor (default 0.88)")

    # Heavy cargo stone container command
    stone = commands.add_parser("stone-container", help="Calculate 20GP heavy-cargo shipping container capacity for stone/slabs")
    stone.add_argument("--area", type=float, required=True, help="Total area in square meters (m²)")
    stone.add_argument("--thickness", type=float, default=20.0, help="Slab/paver thickness in mm (e.g. 20, 30)")
    stone.add_argument("--density", type=float, default=2620.0, help="Material bulk density in kg/m³ (default: 2620 for limestone)")
    stone.add_argument("--payload", type=float, default=26500.0, help="Max 20GP payload in kg (default: 26500)")

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

        if args.command == "safe-url":
            print(safe_urljoin(args.domain, args.path))
            return 0

        if args.command == "container":
            result = estimate_container(args.length, args.width, args.height, args.weight, args.pcs, args.efficiency)
            print(json.dumps(result, indent=2))
            return 0

        if args.command == "stone-container":
            result = estimate_stone_container(args.area, args.thickness, args.density, max_payload_kg=args.payload)
            print(json.dumps(result, indent=2))
            return 0

        self_test()
        return 0
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
