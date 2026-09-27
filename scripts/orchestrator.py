#!/usr/bin/env python3
"""
Master Orchestrator Pipeline
One-command synthesis from:
- Logo (image/SVG)
- Brief intro text (50-100 words)
- Brand name
- Industry ID (one of 12 supported or custom)
- Domain & contact email

Outputs:
1. Full Brand Visual Identity Tokens & CSS (tokens.css, brand_tokens.json)
2. Complete 21-Module Export KB Suite (export_kb.json, 00_cheat_sheet.md, missing_data_queues.json)
3. 5,000+ Word LLMS.txt & 4 AI Discovery Endpoints
4. High-conversion Bento Grid HTML Pages (index, capabilities, products, certifications, oem_odm, contact)
5. WebMCP 2026 Declarative Forms & Live Sourcing Estimator JS
6. 100/100 GEO Audit Verification Report
"""

import os
import sys
import argparse
import subprocess


def run_cmd(cmd: list):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running {' '.join(cmd)}:")
        print(res.stderr)
        sys.exit(res.returncode)
    else:
        if res.stdout.strip():
            print(res.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="Master B2B Export Brand Website Generator")
    parser.add_argument("--name", required=True, help="Brand Name (e.g. Apex Precision Machinery)")
    parser.add_argument("--intro", required=True, help="Brief company introduction (50-100 words)")
    parser.add_argument("--industry", default="machinery", help="Target industry ID (e.g. machinery, stone_cladding, footwear, etc.)")
    parser.add_argument("--domain", default="apexmachinery.com", help="Target official domain")
    parser.add_argument("--email", default="sales@apexmachinery.com", help="Official contact email")
    parser.add_argument("--logo", default="dummy_logo.png", help="Path to company logo image (optional)")
    parser.add_argument("--out", default="./output_brand_site", help="Output directory")

    args = parser.parse_args()
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    print("\n" + "="*70)
    print(f"  LAUNCHING B2B GLOBAL BRAND SITE MASTER GENERATOR")
    print(f"  Brand: {args.name} | Industry: {args.industry} | Domain: {args.domain}")
    print("="*70 + "\n")

    # Step 1: Extract Brand DNA & Tokens
    print(">>> [Step 1/5] Extracting Brand DNA & Generating Design Tokens...")
    extract_script = os.path.join(scripts_dir, "extract_brand_dna.py")
    run_cmd([sys.executable, extract_script, args.logo, args.name, out_dir])

    # Step 2: Synthesize 21-Module Export KB
    print("\n>>> [Step 2/5] Synthesizing 21-Module RenWork Export Knowledge Base...")
    kb_script = os.path.join(scripts_dir, "kb_synthesizer.py")
    run_cmd([sys.executable, kb_script, args.name, args.intro, args.industry, args.domain, args.email, out_dir])

    # Step 3: Compile LLMS.txt, AI Endpoints & Schema.org
    print("\n>>> [Step 3/5] Compiling 5,000+ Word LLMS.txt & 4 AI Discovery Endpoints...")
    llms_script = os.path.join(scripts_dir, "llms_geo_compiler.py")
    kb_json = os.path.join(out_dir, "export_kb.json")
    run_cmd([sys.executable, llms_script, kb_json, args.domain, out_dir])

    # Step 4: Compile High-Conversion B2B Responsive Pages
    print("\n>>> [Step 4/5] Compiling Responsive Bento Pages & WebMCP Components...")
    site_script = os.path.join(scripts_dir, "site_compiler.py")
    tokens_json = os.path.join(out_dir, "brand_tokens.json")
    run_cmd([sys.executable, site_script, kb_json, tokens_json, args.domain, out_dir])

    # Step 5: Execute 100/100 SEO & GEO Quality Audit
    print("\n>>> [Step 5/5] Executing 100/100 SEO & GEO Automated Verification Gate...")
    val_script = os.path.join(scripts_dir, "validate_site_100.py")
    run_cmd([sys.executable, val_script, out_dir])

    print("\n" + "="*70)
    print(f"  SUCCESS! FULL B2B BRAND INDEPENDENT SITE GENERATED AT:")
    print(f"  {out_dir}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
