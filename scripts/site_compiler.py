#!/usr/bin/env python3
"""
B2B Global Brand Site Compiler
Compiles responsive HTML5 pages, clean extensionless canonical links, WebMCP form annotations,
Schema.org JSON-LD, sitemap.xml, and robots.txt.
"""

import os
import sys
import json
import shutil
from typing import Dict, Any


def get_nav_html(brand_name: str, active_page: str) -> str:
    links = [
        ("Home", "/"),
        ("Capabilities", "/capabilities"),
        ("Products", "/products_catalog"),
        ("Certifications", "/certifications"),
        ("OEM/ODM", "/oem_odm"),
        ("Contact", "/contact")
    ]
    nav_items = []
    for title, url in links:
        cls = "active" if url == active_page else ""
        nav_items.append(f'<li><a href="{url}" class="{cls}">{title}</a></li>')

    return f"""
  <header class="site-header">
    <div class="container header-inner">
      <a href="/" class="brand-logo-wrap">
        <span class="brand-text">{brand_name}</span>
      </a>
      <nav>
        <ul class="nav-links">
          {''.join(nav_items)}
        </ul>
      </nav>
      <div class="header-actions">
        <a href="#sampleKitSection" class="btn btn-primary">Request Sample Box</a>
      </div>
    </div>
  </header>
"""


def get_footer_html(brand_name: str, domain: str, email: str, ind_name: str) -> str:
    return f"""
  <footer style="background: #0F172A; color: #94A3B8; padding: 4rem 0 2rem; border-top: 1px solid #1E293B;">
    <div class="container" style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 3rem; margin-bottom: 3rem;">
      <div>
        <h3 style="color: #FFFFFF; margin-bottom: 1rem; font-size: 1.25rem;">{brand_name}</h3>
        <p style="font-size: 0.9375rem; line-height: 1.6; max-width: 320px;">
          ISO 9001 certified global manufacturing enterprise delivering export-grade {ind_name} with verified laboratory test certificates.
        </p>
      </div>
      <div>
        <h4 style="color: #FFFFFF; margin-bottom: 1rem; font-size: 0.9375rem; text-transform: uppercase;">Direct Links</h4>
        <ul style="list-style: none; font-size: 0.875rem; line-height: 2;">
          <li><a href="/capabilities">Smart Manufacturing</a></li>
          <li><a href="/products_catalog">Master Catalog</a></li>
          <li><a href="/certifications">Audit & Compliance</a></li>
          <li><a href="/oem_odm">Custom Prototyping</a></li>
        </ul>
      </div>
      <div>
        <h4 style="color: #FFFFFF; margin-bottom: 1rem; font-size: 0.9375rem; text-transform: uppercase;">AI & Machine Data</h4>
        <ul style="list-style: none; font-size: 0.875rem; line-height: 2;">
          <li><a href="/llms.txt" target="_blank">llms.txt (AI Index)</a></li>
          <li><a href="/ai/summary.json" target="_blank">/ai/summary.json</a></li>
          <li><a href="/ai/faq.json" target="_blank">/ai/faq.json</a></li>
          <li><a href="/ai/service.json" target="_blank">/ai/service.json</a></li>
        </ul>
      </div>
      <div>
        <h4 style="color: #FFFFFF; margin-bottom: 1rem; font-size: 0.9375rem; text-transform: uppercase;">Direct Contact</h4>
        <p style="font-size: 0.875rem; line-height: 1.8;">
          Email: <a href="mailto:{email}" style="color: #FFFFFF;">{email}</a><br>
          Export Port: Ningbo / Shanghai / Xiamen<br>
          Incoterms: FOB, CIF, DAP
        </p>
      </div>
    </div>
    <div class="container" style="border-top: 1px solid #1E293B; padding-top: 1.5rem; text-align: center; font-size: 0.8125rem;">
      <p>&copy; 2026 {brand_name} Co., Ltd. All Rights Reserved. Built with RenWork 100/100 GEO Architecture.</p>
    </div>
  </footer>

  <!-- Mobile 3-Button Bottom Sticky Thumb-Dock -->
  <aside class="mobile-thumb-dock">
    <div class="dock-actions">
      <a href="https://wa.me/8613800000000?text=Hello%20{brand_name}%2C%20inquiry%20regarding%20{ind_name}" class="dock-btn dock-btn-whatsapp" target="_blank" rel="noopener">
        <span>💬 WhatsApp</span>
      </a>
      <a href="#sampleKitSection" class="dock-btn dock-btn-sample">
        <span>📦 Sample Kit</span>
      </a>
      <a href="/docs/engineering-specs.md" class="dock-btn dock-btn-spec" target="_blank">
        <span>📥 Spec PDF</span>
      </a>
    </div>
  </aside>
"""


def compile_index(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]
    m = kb["modules"]
    standards = m["06_certification_compliance"]["active_certifications"]
    flagship = m["04_product_catalog"]["flagship_series"][0]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{b} | Certified Export Manufacturer of {ind_name}</title>
  <meta name="description" content="{m['02_company_identity']['intro_100_words']}">
  <link rel="canonical" href="https://{domain}/">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/")}

  <main id="main-content">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container">
        <div class="hero-badges">
          {''.join([f'<span class="badge-cert">✓ {s}</span>' for s in standards])}
          <span class="badge-cert">AQL 0.65 Certified</span>
        </div>
        <h1 class="hero-title">{b}: Precision Engineered {ind_name}</h1>
        <p class="hero-desc">
          {m['03_brand_messaging']['unique_value_proposition']} Backed by 28,000 m² smart production infrastructure and accredited laboratory test dossiers.
        </p>
        <div class="hero-ctas">
          <a href="#sampleKitSection" class="btn btn-primary">Request Complimentary Sample Box</a>
          <a href="#sourcingCalculatorSection" class="btn btn-outline">Calculate Container Load & Freight</a>
        </div>
      </div>
    </section>

    <!-- Industrial Bento Grid -->
    <section class="container" style="padding: 4rem 0;">
      <div class="section-title-wrap">
        <h2 class="section-title">Verified Industrial Manufacturing Credentials</h2>
        <p class="section-subtitle">Real factory data, verified laboratory thresholds, and zero marketing fluff.</p>
      </div>

      <div class="bento-grid">
        <div class="bento-card bento-col-8">
          <div class="bento-metric-large">{m['02_company_identity']['facility_area_sqm']:,} m²</div>
          <h3 class="bento-card-title">Intelligent Smart Manufacturing Base</h3>
          <p class="bento-card-desc">
            Equipped with 4 continuous automated lines integrating sub-second in-line laser inspection. Delivering {m['02_company_identity']['annual_capacity']} with 99.4% on-time shipment compliance.
          </p>
        </div>

        <div class="bento-card bento-col-4">
          <div class="bento-metric-large">{m['07_commercial_delivery']['lead_times']['sample']}</div>
          <h3 class="bento-card-title">Rapid Prototyping</h3>
          <p class="bento-card-desc">
            Direct 3D CAD/CAM tooling turnaround with full dimensional CMM inspection dossiers.
          </p>
        </div>

        <div class="bento-card bento-col-4">
          <div class="bento-metric-large">AQL 0.65</div>
          <h3 class="bento-card-title">8-Stage Quality Gates</h3>
          <p class="bento-card-desc">
            Zero-defect protocol from raw inbound spectrometry to pre-shipment container seal audits.
          </p>
        </div>

        <div class="bento-card bento-col-4">
          <div class="bento-metric-large">100%</div>
          <h3 class="bento-card-title">Compliance Traceability</h3>
          <p class="bento-card-desc">
            Full compliance with {', '.join(standards[:3])}. Certified test reports available on demand.
          </p>
        </div>

        <div class="bento-card bento-col-4">
          <div class="bento-metric-large">40+</div>
          <h3 class="bento-card-title">Global Export Countries</h3>
          <p class="bento-card-desc">
            Long-term supply agreements with Tier-1 general contractors and brand specifiers across NA, EU, and Middle East.
          </p>
        </div>
      </div>
    </section>

    <!-- Interactive Sourcing Calculator -->
    <section id="sourcingCalculatorSection" class="container">
      <div class="calc-section">
        <div class="calc-grid">
          <div>
            <h2 class="section-title" style="text-align: left; margin-bottom: 1rem;">Interactive Ocean Container Estimator</h2>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">
              Simulate container volume displacement, weight limits, and freight packing efficiency for export orders.
            </p>

            <form id="containerEstimatorForm" 
                  toolname="calculateContainerLandedCost" 
                  tooldescription="Interactive procurement calculator to compute ocean shipping container CBM utilization, gross weight, and estimated FOB/CIF unit cost">
              <div class="calc-form-group">
                <label for="targetSku">Select Product Specification</label>
                <select id="targetSku" class="calc-select" toolparamdescription="Product model identifier">
                  <option value="{flagship['model']}" data-cbm="0.015" data-weight="1.2">{flagship['model']} - {flagship['title']}</option>
                  <option value="EXP-STANDARD" data-cbm="0.012" data-weight="0.95">EXP-STANDARD - Compact Version</option>
                </select>
              </div>

              <div class="calc-form-group">
                <label for="orderQty">Order Quantity (Units)</label>
                <input type="number" id="orderQty" class="calc-input" value="1000" min="100" step="100" toolparamdescription="Order quantity in units">
              </div>

              <div class="calc-form-group">
                <label for="containerType">Target Ocean Container Specification</label>
                <select id="containerType" class="calc-select" toolparamdescription="Container spec 20GP or 40HQ">
                  <option value="40HQ">40' High Cube (40HQ - 68 m³ / 26,000 kg)</option>
                  <option value="20GP">20' General Purpose (20GP - 28 m³ / 18,000 kg)</option>
                </select>
              </div>
            </form>
          </div>

          <div class="calc-results-box">
            <h3 style="margin-bottom: 1.5rem; font-size: 1.25rem;">Estimated Sourcing Metrics</h3>
            <div class="result-row">
              <span>Total Volume Displacement:</span>
              <span id="resCbm" class="result-val">15.00 m³</span>
            </div>
            <div class="result-row">
              <span>Estimated Gross Cargo Weight:</span>
              <span id="resWeight" class="result-val">1,200.0 kg</span>
            </div>
            <div class="result-row">
              <span>Container Utilization Rate:</span>
              <span id="resFill" class="result-val">22% Capacity</span>
            </div>
            <div class="result-row">
              <span>Required Maritime Units:</span>
              <span id="resContainers" class="result-val">0.2 × 40HQ</span>
            </div>
            <p style="font-size: 0.8125rem; color: var(--text-muted); margin-top: 1.5rem;">
              * Calculations are simulated based on standard Euro-pallet stacking. Final stowage plans are verified prior to container loading.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- WebMCP Sample Kit Form -->
    <section id="sampleKitSection" class="container">
      <div class="webmcp-form-card">
        <div style="text-align: center; max-width: 680px; margin: 0 auto 2.5rem;">
          <h2 class="section-title">Request Verified B2B Trade Sample Box</h2>
          <p style="color: var(--text-secondary);">
            {m['18_sales_content_templates']['sample_kit_program']['title']}. Dispatched within 24 business hours via DHL Express with full laboratory testing dossiers.
          </p>
        </div>

        <form id="sampleKitForm" 
              action="/api/sample-request" 
              method="POST" 
              toolname="orderTradeSampleKit" 
              tooldescription="Submit international courier address to receive verified physical B2B sample kit with factory test dossiers" 
              toolautosubmit>
          <div class="form-row">
            <div>
              <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Company / Organization Name</label>
              <input type="text" class="form-control" name="company_name" placeholder="e.g. Apex Industrial Corp" required toolparamdescription="Corporate entity name">
            </div>
            <div>
              <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Procurement Officer / Specifier Name</label>
              <input type="text" class="form-control" name="contact_name" placeholder="Full name" required toolparamdescription="Contact person name">
            </div>
          </div>

          <div class="form-row">
            <div>
              <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Corporate Email</label>
              <input type="email" class="form-control" name="email" placeholder="name@company.com" required toolparamdescription="Official company email">
            </div>
            <div>
              <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Application / Industry Sector</label>
              <input type="text" class="form-control" name="sector" value="{ind_name}" toolparamdescription="Application industry">
            </div>
          </div>

          <div>
            <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">International Shipping Address (DHL Express Delivery)</label>
            <textarea class="form-control" rows="3" name="delivery_address" placeholder="Street, Suite/Floor, City, Postal Code, Country" required toolparamdescription="Complete international courier address"></textarea>
          </div>

          <div style="text-align: center; margin-top: 1.5rem;">
            <button type="submit" class="btn btn-primary" style="padding: 0.875rem 2.5rem; font-size: 1rem;">
              Dispatch Free Trade Sample Box
            </button>
          </div>
        </form>
      </div>
    </section>

    <!-- Technical FAQ (RAG Answer Capsules) -->
    <section class="container" style="padding-bottom: 5rem;">
      <div class="section-title-wrap">
        <h2 class="section-title">Technical Sourcing & Compliance FAQ</h2>
        <p class="section-subtitle">Answer-First technical clarifications for engineering directors and procurement committees.</p>
      </div>

      <div style="max-width: 860px; margin: 0 auto;">
        <div class="faq-item">
          <div class="faq-q">Q: What quality assurance testing gates are enforced on production runs?</div>
          <div class="faq-a">
            {b} enforces an 8-stage inline inspection protocol aligned with MIL-STD-105E AQL 0.65 thresholds. From raw material spectrometry to ultrasonic micro-crack detection, each production lot is documented in traceable Mill Test Certificates (MTC).
          </div>
        </div>

        <div class="faq-item">
          <div class="faq-q">Q: What is the typical MOQ and delivery window for customized private label orders?</div>
          <div class="faq-a">
            Standard OEM production MOQ begins at {m['07_commercial_delivery']['standard_moq']}. Rapid 3D prototyping samples dispatch within 7–10 days, while full container load shipments dispatch in 25–30 calendar days.
          </div>
        </div>

        <div class="faq-item">
          <div class="faq-q">Q: What is your payment policy and how do you protect against wire transfer fraud?</div>
          <div class="faq-a">
            All wire transfers must be executed exclusively to our registered corporate bank account under the name "{b} Co., Ltd.". We never alter bank details via email. Any bank modification alert requires dual video and telephone confirmation prior to remittance.
          </div>
        </div>
      </div>
    </section>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
  <script src="/js/sourcing_estimator.js"></script>
</body>
</html>
"""


def compile_capabilities(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]
    m = kb["modules"]

    gates_html = "".join([f'<li style="margin-bottom: 1rem; padding-left: 0.5rem;"><strong>{gate}</strong></li>' for gate in m['05_manufacturing_quality']['qc_inspection_gates']])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Manufacturing & Quality Assurance | {b}</title>
  <meta name="description" content="Explore {b}'s 28,000 m² smart production base, 8-stage inline quality gates, and AQL 0.65 testing laboratory.">
  <link rel="canonical" href="https://{domain}/capabilities">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/capabilities")}

  <main id="main-content" class="container" style="padding: 4rem 1.5rem;">
    <h1 class="hero-title">Smart Manufacturing & Quality Assurance</h1>
    <p class="hero-desc">
      {m['02_company_identity']['intro_300_words']}
    </p>

    <div class="bento-grid" style="margin: 3rem 0;">
      <div class="bento-card bento-col-6">
        <h2 class="bento-card-title">Automated Production Lines</h2>
        <p class="bento-card-desc">
          Operating 4 synchronized lines with sub-second feedback loops and high-precision tooling offsets.
        </p>
      </div>
      <div class="bento-card bento-col-6">
        <h2 class="bento-card-title">In-House Testing Rig</h2>
        <p class="bento-card-desc">
          Equipped for continuous mechanical stress, freeze-thaw thermal cycling, and QUV weathering simulation.
        </p>
      </div>
    </div>

    <section style="background: #ffffff; border: 1px solid var(--brand-border); border-radius: var(--radius-md); padding: 3rem; margin: 3rem 0;">
      <h2 style="font-size: 1.75rem; margin-bottom: 1.5rem;">8-Stage Strict Quality Inspection Gates</h2>
      <ol style="line-height: 1.8; color: var(--text-secondary); padding-left: 1.5rem;">
        {gates_html}
      </ol>
    </section>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
</body>
</html>
"""


def compile_products(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]
    m = kb["modules"]
    series = m["04_product_catalog"]["flagship_series"]

    cards = []
    for p in series:
        spec_rows = "".join([f'<tr><td style="padding:0.5rem; border:1px solid #E2E8F0; font-weight:600;">{k.replace("_", " ").title()}</td><td style="padding:0.5rem; border:1px solid #E2E8F0;">{v}</td></tr>' for k, v in p["specs"].items()])
        cards.append(f"""
        <div class="bento-card bento-col-6">
          <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">{p['title']}</h2>
          <p style="color: var(--brand-primary); font-family: var(--font-mono); font-weight: 700; margin-bottom: 1rem;">Model: {p['model']}</p>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 1.5rem; font-size: 0.875rem;">
            {spec_rows}
          </table>
          <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1.5rem;">
            Standard MOQ: <strong>{p['moq']}</strong> | Lead Time: <strong>{p['lead_time']}</strong>
          </p>
          <a href="/contact" class="btn btn-primary" style="width: 100%;">Inquire for Master Quotation</a>
        </div>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Product Catalog & Specifications | {b}</title>
  <meta name="description" content="Explore {b}'s certified {ind_name} models, dimensional specifications, and wholesale MOQ tiers.">
  <link rel="canonical" href="https://{domain}/products_catalog">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/products_catalog")}

  <main id="main-content" class="container" style="padding: 4rem 1.5rem;">
    <h1 class="hero-title">Master Product Catalog & Engineering Tolerances</h1>
    <p class="hero-desc">
      Certified technical parameters in dual metric and imperial formats. Every series is supported by downloadable 3D CAD/STEP models and Mill Test Certificates.
    </p>

    <div class="bento-grid" style="margin-top: 3rem;">
      {''.join(cards)}
    </div>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
</body>
</html>
"""


def compile_certifications(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]
    m = kb["modules"]
    standards = m["06_certification_compliance"]["active_certifications"]

    certs_rows = "".join([f'<tr><td style="padding:1rem; border:1px solid #E2E8F0; font-weight:700;">{s}</td><td style="padding:1rem; border:1px solid #E2E8F0;">Active Compliance</td><td style="padding:1rem; border:1px solid #E2E8F0;">Third-Party Accredited Testing Body</td><td style="padding:1rem; border:1px solid #E2E8F0;"><span style="color:#0F52BA; font-weight:600;">Verified Dossier</span></td></tr>' for s in standards])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>International Certifications & Regulatory Ledger | {b}</title>
  <meta name="description" content="Official regulatory compliance, audit reports, and test certificates for {b}'s {ind_name}.">
  <link rel="canonical" href="https://{domain}/certifications">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/certifications")}

  <main id="main-content" class="container" style="padding: 4rem 1.5rem;">
    <h1 class="hero-title">International Certifications & Audit Ledger</h1>
    <p class="hero-desc">
      Uncompromising commitment to global regulatory compliance, structural testing, and commercial transparency.
    </p>

    <div style="background: #ffffff; border: 1px solid var(--brand-border); border-radius: var(--radius-md); padding: 2rem; margin: 3rem 0;">
      <table style="width: 100%; border-collapse: collapse; text-align: left;">
        <thead>
          <tr style="background: var(--brand-surface);">
            <th style="padding: 1rem; border: 1px solid #E2E8F0;">Standard / Regulation</th>
            <th style="padding: 1rem; border: 1px solid #E2E8F0;">Status</th>
            <th style="padding: 1rem; border: 1px solid #E2E8F0;">Testing Authority</th>
            <th style="padding: 1rem; border: 1px solid #E2E8F0;">Verification Link</th>
          </tr>
        </thead>
        <tbody>
          {certs_rows}
        </tbody>
      </table>
    </div>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
</body>
</html>
"""


def compile_oem_odm(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]
    m = kb["modules"]
    tiers = m["16_solution_quotation"]["good_better_best_tiers"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OEM / ODM Custom Prototyping & Tiers | {b}</title>
  <meta name="description" content="Discover {b}'s Good/Better/Best quotation tiers, custom tooling SOP, and private label branding services.">
  <link rel="canonical" href="https://{domain}/oem_odm">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/oem_odm")}

  <main id="main-content" class="container" style="padding: 4rem 1.5rem;">
    <h1 class="hero-title">OEM / ODM Custom Engineering & Pricing Tiers</h1>
    <p class="hero-desc">
      From drawing conceptualization to full-container delivery: choose your collaboration tier to fit budget and market positioning.
    </p>

    <div class="bento-grid" style="margin-top: 3rem;">
      <div class="bento-card bento-col-4">
        <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Tier 1: {tiers['good']['name']}</h2>
        <p style="color: var(--brand-primary); font-weight: 700; margin-bottom: 1rem;">MOQ: {tiers['good']['moq']}</p>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{tiers['good']['desc']}</p>
        <p style="font-size: 0.875rem;">Lead Time: {tiers['good']['lead_time']}</p>
      </div>

      <div class="bento-card bento-col-4" style="border: 2px solid var(--brand-primary);">
        <span style="background: var(--brand-primary); color: #fff; font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.5rem; border-radius: 4px; display: inline-block; margin-bottom: 0.5rem;">RECOMMENDED</span>
        <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Tier 2: {tiers['better']['name']}</h2>
        <p style="color: var(--brand-primary); font-weight: 700; margin-bottom: 1rem;">MOQ: {tiers['better']['moq']}</p>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{tiers['better']['desc']}</p>
        <p style="font-size: 0.875rem;">Lead Time: {tiers['better']['lead_time']}</p>
      </div>

      <div class="bento-card bento-col-4">
        <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Tier 3: {tiers['best']['name']}</h2>
        <p style="color: var(--brand-primary); font-weight: 700; margin-bottom: 1rem;">MOQ: {tiers['best']['moq']}</p>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">{tiers['best']['desc']}</p>
        <p style="font-size: 0.875rem;">Lead Time: {tiers['best']['lead_time']}</p>
      </div>
    </div>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
</body>
</html>
"""


def compile_contact(kb: Dict[str, Any], schema_json: str, domain: str) -> str:
    b = kb["metadata"]["brand_name"]
    ind_name = kb["metadata"]["industry_name"]
    email = kb["metadata"]["official_email"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Direct B2B Commercial Inquiry & RFQ | {b}</title>
  <meta name="description" content="Submit formal engineering RFQ or sample box dispatch request directly to {b}'s export department.">
  <link rel="canonical" href="https://{domain}/contact">
  <link rel="stylesheet" href="/css/tokens.css">
  <link rel="stylesheet" href="/css/b2b-industrial-core.css">
  <script type="application/ld+json">
  {schema_json}
  </script>
</head>
<body>
  {get_nav_html(b, "/contact")}

  <main id="main-content" class="container" style="padding: 4rem 1.5rem;">
    <h1 class="hero-title">Direct Commercial RFQ & Technical Sourcing</h1>
    <p class="hero-desc">
      Connect directly with our senior application engineering team for formal price schedules, drawing reviews, and custom tooling analysis.
    </p>

    <div class="webmcp-form-card" style="margin: 2rem 0;">
      <form id="rfqForm" 
            action="/api/rfq-submit" 
            method="POST" 
            toolname="requestB2BQuotation" 
            tooldescription="Submit detailed commercial RFQ and technical specifications for formal export quotation" 
            toolautosubmit>
        <div class="form-row">
          <div>
            <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Company Name</label>
            <input type="text" class="form-control" name="company_name" required toolparamdescription="Corporate name">
          </div>
          <div>
            <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Contact Name & Job Title</label>
            <input type="text" class="form-control" name="contact_name" required toolparamdescription="Decision maker name">
          </div>
        </div>

        <div class="form-row">
          <div>
            <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Work Email</label>
            <input type="email" class="form-control" name="work_email" required toolparamdescription="Official email">
          </div>
          <div>
            <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Estimated Order Volume</label>
            <input type="text" class="form-control" name="volume" placeholder="e.g. 5,000 units or 1x 40HQ" toolparamdescription="Estimated order volume">
          </div>
        </div>

        <div>
          <label style="display:block; margin-bottom:0.5rem; font-weight:600; font-size:0.875rem;">Project Details & Drawing Specs</label>
          <textarea class="form-control" rows="4" name="project_details" placeholder="Describe dimensional specifications, required standards (ASTM/CE/ISO), and target destination port." required toolparamdescription="Detailed requirements"></textarea>
        </div>

        <button type="submit" class="btn btn-primary" style="padding: 0.875rem 2rem;">
          Submit Formal B2B RFQ
        </button>
      </form>
    </div>
  </main>

  {get_footer_html(b, domain, email, ind_name)}
</body>
</html>
"""


def compile_sitemap_xml(domain: str, pages: list) -> str:
    urls_xml = []
    for p in pages:
        path = "" if p == "index" else f"/{p}"
        urls_xml.append(f"""  <url>
    <loc>https://{domain}{path}</loc>
    <lastmod>2026-09-27</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{"1.0" if p == "index" else "0.8"}</priority>
  </url>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls_xml)}
</urlset>
"""


def compile_robots_txt(domain: str) -> str:
    return f"""User-agent: *
Allow: /

# Generative AI Search Bots & Answer Crawlers
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: GoogleOther
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Applebot-Extended
Allow: /

# Machine Discovery & Sitemaps
Sitemap: https://{domain}/sitemap.xml
llms-txt: https://{domain}/llms.txt
llms-full: https://{domain}/llms-full.txt
"""


def main():
    if len(sys.argv) < 5:
        print("Usage: python3 site_compiler.py <export_kb_json> <brand_tokens_json> <domain> <output_dir>")
        sys.exit(1)

    kb_path = sys.argv[1]
    tokens_path = sys.argv[2]
    domain = sys.argv[3]
    out_dir = sys.argv[4]

    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)

    # Read schema graph if exists
    schema_path = os.path.join(out_dir, "schema_graph.json")
    schema_json = "{}"
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_json = f.read()

    os.makedirs(out_dir, exist_ok=True)
    css_dir = os.path.join(out_dir, "css")
    js_dir = os.path.join(out_dir, "js")
    os.makedirs(css_dir, exist_ok=True)
    os.makedirs(js_dir, exist_ok=True)

    # Copy template assets
    templates_dir = os.path.join(os.path.dirname(__file__), "../templates")
    src_css = os.path.join(templates_dir, "assets/css/b2b-industrial-core.css")
    src_js = os.path.join(templates_dir, "assets/js/sourcing_estimator.js")
    if os.path.exists(src_css):
        shutil.copy(src_css, os.path.join(css_dir, "b2b-industrial-core.css"))
    if os.path.exists(src_js):
        shutil.copy(src_js, os.path.join(js_dir, "sourcing_estimator.js"))

    # Write HTML pages
    pages = {
        "index": compile_index(kb, schema_json, domain),
        "capabilities": compile_capabilities(kb, schema_json, domain),
        "products_catalog": compile_products(kb, schema_json, domain),
        "certifications": compile_certifications(kb, schema_json, domain),
        "oem_odm": compile_oem_odm(kb, schema_json, domain),
        "contact": compile_contact(kb, schema_json, domain)
    }

    for name, content in pages.items():
        page_file = os.path.join(out_dir, f"{name}.html")
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(content)

    # Generate sitemap.xml & robots.txt
    sitemap = compile_sitemap_xml(domain, list(pages.keys()))
    with open(os.path.join(out_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)

    robots = compile_robots_txt(domain)
    with open(os.path.join(out_dir, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"✓ All 6 Core Pages Compiled: {list(pages.keys())}")
    print(f"✓ Sitemap & Robots Generated: sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
