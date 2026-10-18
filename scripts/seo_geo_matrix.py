#!/usr/bin/env python3
"""B2B SEO/GEO keyword tree, topic cluster stitcher, GEO + Zero-AI-Slop dual auditor, 4-phase workspace orchestrator (deeply fused with cnproduct/b2b-global-brand-site-master 21-module KB, M0/M1/M2 maturity, 9 industry blueprint fields, asset register & edge protection), SKU catalog auditor, B2B editorial syndication generator, and 7-state backlink ledger (V4.0).
"""
import argparse
import csv
import html.parser
import io
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BACKLINK_STATES = (
    'candidate',
    'qualified',
    'filled',
    'submitted',
    'public',
    'indexed',
    'rel_verified',
)

AI_SLOP_PHRASES = (
    'in today\'s fast-paced',
    'in the ever-evolving landscape',
    'look no further',
    'unlock the full potential',
    'revolutionize your',
    'seamless integration',
    'cutting-edge solution',
    'delve into',
    'testament to',
    'world-class',
    'best-in-class',
)

UI_SLOP_PATTERNS = (
    ('bg-clip-text', 'Neon gradient text highlight (violates Anti-AI-Slop Rule #1: No Neon Text Gradients)'),
    ('text-transparent', 'Transparent gradient headline gimmick (violates Anti-AI-Slop Rule #1)'),
    ('shadow-xl', 'Heavy diffuse drop shadow card (violates Anti-AI-Slop Rule #2: use 1px subtle border or tonal shift)'),
    ('shadow-2xl', 'Heavy diffuse drop shadow card (violates Anti-AI-Slop Rule #2: use 1px subtle border or tonal shift)'),
    ('#777', 'Pure flat hex grey #777 (violates Anti-AI-Slop Rule #6: use OKLCH color-mix tinted neutrals)'),
    ('#888', 'Pure flat hex grey #888 (violates Anti-AI-Slop Rule #6: use OKLCH color-mix tinted neutrals)'),
    ('#999', 'Pure flat hex grey #999 (violates Anti-AI-Slop Rule #6: use OKLCH color-mix tinted neutrals)'),
)

B2B_VISUAL_ARCHETYPES = {
    'precision_engineering': {
        'industries': ['machinery', 'components', 'electronics', 'automotive', 'energy'],
        'data_layout': 'engineering',
        'palette_direction': 'High-contrast slate, anodized steel, and safety amber/cobalt interactive accents (OKLCH tinted neutrals)',
        'oklch_hue': 250,
        'typography_pairing': 'Space Grotesk / Clash Display (headings) + Inter / Plus Jakarta Sans (body) + JetBrains Mono (tabular-nums spec readouts)',
        'signature_components': ['First-viewport interactive spec/tolerance filter workbench', 'Dimensional tolerance table with tabular-nums', 'Multi-SKU RFQ Basket Drawer'],
    },
    'cleanroom_regulatory': {
        'industries': ['medical', 'hygiene', 'chemicals', 'food'],
        'data_layout': 'evidence',
        'palette_direction': 'Clinical pure surface, deep laboratory navy, and high-legibility emerald/cobalt verification badges',
        'oklch_hue': 235,
        'typography_pairing': 'Plus Jakarta Sans (headings) + Inter (body) + Geist Mono (lot/batch & test standard codes)',
        'signature_components': ['First-viewport BOM core & absorbency/grade interactive selector', 'Certification scope & validity verification strip', 'Batch traceability & AQL protocol card'],
    },
    'architectural_material': {
        'industries': ['building-materials', 'limestone', 'sanitaryware', 'furniture', 'bento', 'appliances'],
        'data_layout': 'materials',
        'palette_direction': 'Warm mineral stone, brushed stainless neutral, and deep architectural charcoal',
        'oklch_hue': 240,
        'typography_pairing': 'Instrument Serif / General Sans (headings) + Switzer / Inter (body) + JetBrains Mono (dimensions & container CBM)',
        'signature_components': ['First-viewport interactive material swatch + 20GP/40HQ load workbench', 'Accessible material/finish swatch switcher (WCAG 2.2 roving tabindex)', 'Cross-section structural callout'],
    },
    'agile_oem_lookbook': {
        'industries': ['apparel', 'footwear', 'bags', 'packaging', 'beauty', 'toys-sports', 'pet-products'],
        'data_layout': 'oem',
        'palette_direction': 'Editorial high-contrast neutral canvas with bespoke brand-extracted accent token',
        'oklch_hue': 260,
        'typography_pairing': 'Syne / General Sans (headings) + Plus Jakarta Sans (body) + JetBrains Mono (GSM/oz, MOQ, carton specs)',
        'signature_components': ['First-viewport interactive OEM customization configurator (material, logo craft, packaging)', 'Sampling lead-time & tooling timeline', 'Multi-SKU Sample Kit Basket Drawer'],
    },
}

B2B_INTENT_BRANCHES = [
    {
        'branch_id': 'oem_odm_custom',
        'intent_label': 'OEM / ODM & Private Label Manufacturing',
        'buyer_stage': 'Supplier Qualification & Custom Briefing',
        'modifiers': ['oem manufacturer', 'odm supplier', 'private label factory', 'custom tooling bulk', 'bespoke specification'],
        'target_page_type': 'oem-odm',
        'target_clean_url': '/oem-odm/',
        'kb_modules_required': ['04_product_system', '05_manufacturing_quality', '16_solution_sampling'],
        'primary_cta_tier': 'Tier 2: Custom BOM / Drawing & Sample RFQ',
    },
    {
        'branch_id': 'manufacturer_supplier',
        'intent_label': 'Direct Factory & Certified Industrial Supplier',
        'buyer_stage': 'Vendor Shortlisting',
        'modifiers': ['manufacturer', 'factory direct', 'industrial supplier', 'iso certified manufacturer', 'export factory'],
        'target_page_type': 'home / capabilities',
        'target_clean_url': '/',
        'kb_modules_required': ['02_company_identity', '05_manufacturing_quality', '06_certification_compliance'],
        'primary_cta_tier': 'Tier 3: Factory Audit & Volume Production Quote',
    },
    {
        'branch_id': 'bulk_wholesale_logistics',
        'intent_label': 'Bulk Wholesale, MOQ & Container Loading',
        'buyer_stage': 'Commercial & Logistics Evaluation',
        'modifiers': ['bulk wholesale', 'moq', '20gp 40hq container load', 'fob price list', 'export carton specification'],
        'target_page_type': 'products / calculator',
        'target_clean_url': '/products/',
        'kb_modules_required': ['04_product_system', '07_commercial_delivery', '19_fulfillment_aftersales'],
        'primary_cta_tier': 'Tier 3: Container Load & Tiered FOB Quote',
    },
    {
        'branch_id': 'technical_spec_material',
        'intent_label': 'Technical Parameters, Materials & Tolerances',
        'buyer_stage': 'Engineering & Specification Selection',
        'modifiers': ['technical specifications', 'material grade chart', 'dimension tolerance', 'datasheet pdf', 'performance test standard'],
        'target_page_type': 'products / resources',
        'target_clean_url': '/capabilities/',
        'kb_modules_required': ['04_product_system', '05_manufacturing_quality', '06_certification_compliance'],
        'primary_cta_tier': 'Tier 1: Datasheet & Standard Sample Request',
    },
    {
        'branch_id': 'application_solution',
        'intent_label': 'Industry Application & Operating Conditions',
        'buyer_stage': 'Problem-to-Solution Mapping',
        'modifiers': ['for industrial application', 'heavy duty solution', 'operating temperature range', 'engineering selection guide', 'application case'],
        'target_page_type': 'solutions',
        'target_clean_url': '/resources/',
        'kb_modules_required': ['09_icp_personas', '12_scenario_matching', '18_content_assets'],
        'primary_cta_tier': 'Tier 2: Application Engineering Consultation',
    },
    {
        'branch_id': 'comparison_alternative',
        'intent_label': 'Material / Process Trade-off & Comparison',
        'buyer_stage': 'Trade-off Evaluation (High GEO Citation Value)',
        'modifiers': ['vs', 'material comparison table', 'process alternative', 'cost vs performance', 'how to specify for bulk sourcing'],
        'target_page_type': 'resources',
        'target_clean_url': '/resources/',
        'kb_modules_required': ['04_product_system', '11_competitive_intelligence', '17_objection_negotiation'],
        'primary_cta_tier': 'Tier 1: Side-by-Side Spec Sample Kit Request',
    },
]


def load_industries():
    path = ROOT / 'assets/industries.json'
    return json.loads(path.read_text(encoding='utf-8'))['industries']


def get_industry(industry_id):
    for item in load_industries():
        if item['id'] == industry_id:
            return item
    raise ValueError(f'unknown industry: {industry_id}')


def get_visual_archetype(industry_id):
    profile = get_industry(industry_id)
    for arch_id, meta in B2B_VISUAL_ARCHETYPES.items():
        if industry_id in meta['industries']:
            return {'archetype_id': arch_id, 'compiler_data_layout': profile.get('layout', meta['data_layout']), **meta}
    return {'archetype_id': 'precision_engineering', 'compiler_data_layout': profile.get('layout', 'engineering'), **B2B_VISUAL_ARCHETYPES['precision_engineering']}


def assess_project_maturity(project_path):
    """Evaluates whether a B2B project is at M0 (Logo + Intro), M1 (Catalog + Real Photos + Commercial Terms), or M2 (Test Reports + Cases + Search Data)."""
    project_path = Path(project_path)
    cards_file = project_path / 'private/knowledge-cards.json'
    assets_file = project_path / 'private/asset-register.json'
    verified_cards = []
    approved_assets = []
    if cards_file.is_file():
        try:
            cards = json.loads(cards_file.read_text(encoding='utf-8'))
            verified_cards = [c for c in cards if isinstance(c, dict) and c.get('status') in ('verified_fact', 'public_fact') and c.get('public_claim_approved') is True]
        except Exception:
            pass
    if assets_file.is_file():
        try:
            assets = json.loads(assets_file.read_text(encoding='utf-8'))
            approved_assets = [a for a in assets if isinstance(a, dict) and a.get('approval') == 'approved' and a.get('visibility') == 'public']
        except Exception:
            pass
    modules_with_facts = {c.get('module') for c in verified_cards}
    if len(verified_cards) >= 5 and any(m in modules_with_facts for m in ('06_certification_compliance', '14_customer_assets', '20_review_analytics')):
        stage = 'M2'
        summary = 'M2 (Test Reports + Verified Cases + Search Data): Ready for full 10-page release, evidence-backed case pages, and localized market expansion.'
    elif len(verified_cards) >= 1 and len(approved_assets) >= 1:
        stage = 'M1'
        summary = 'M1 (Product Specs + Approved Media + Commercial Terms): Ready for verified product comparison tables, downloadable PDFs, OEM workflow, and HTTP RFQ.'
    else:
        stage = 'M0'
        summary = 'M0 (Logo + Brief Intro Only): Build 6-page noindex draft, category/selection guides, email_draft RFQ, and private/gaps.md checklist without inventing SKUs or certificates.'
    return {
        'maturity_stage': stage,
        'summary': summary,
        'verified_public_fact_cards': len(verified_cards),
        'approved_public_assets': len(approved_assets),
    }


def build_design_tokens_css(industry_id):
    """Generates src/styles/design-tokens.css with Major Third (1.25) clamp() typography, OKLCH tinted neutrals, CJK/RTL rules, tabular-nums, and 12-col asymmetrical grid."""
    arch = get_visual_archetype(industry_id)
    hue = arch.get('oklch_hue', 250)
    return f"""/* B2B Zero AI-Slop Design Tokens ({arch['archetype_id']} | data-layout="{arch['compiler_data_layout']}" | Hue: {hue}) */
:root {{
  /* 1. Major Third (1.25) Fluid Typographic Scale */
  --text-xs: clamp(0.75rem, 0.72rem + 0.15vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.82rem + 0.25vw, 1rem);
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --text-lg: clamp(1.25rem, 1.15rem + 0.5vw, 1.4rem);
  --text-xl: clamp(1.56rem, 1.38rem + 0.9vw, 1.75rem);
  --text-2xl: clamp(1.95rem, 1.68rem + 1.35vw, 2.25rem);
  --text-3xl: clamp(2.44rem, 2.05rem + 1.95vw, 3rem);
  --text-4xl: clamp(3.05rem, 2.45rem + 3vw, 4rem);

  /* 2. Multi-Script Reading Measure Constraints (Latin 65ch / CJK 36em) */
  --measure-prose: 65ch;
  --measure-cjk: 36em;
  --measure-narrow: 45ch;
  --measure-wide: 75ch;

  /* 3. OKLCH Tinted Neutrals (Zero Pure Hex Greys #777/#888/#999) */
  --bg-surface: oklch(0.985 0.006 {hue});
  --bg-elevated: oklch(0.965 0.008 {hue});
  --text-primary: oklch(0.16 0.02 {hue});
  --text-muted: color-mix(in oklch, var(--text-primary) 65%, transparent);
  --border-subtle: color-mix(in oklch, var(--text-primary) 12%, transparent);
  --accent-interactive: oklch(0.46 0.15 {hue});

  /* 4. Strict 2+1 Font Stack */
  --font-heading: 'General Sans', 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-body: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Geist Mono', ui-monospace, SFMono-Regular, monospace;
}}

/* CJK Typography Adaptation (from references/web-design.md) */
:lang(zh), :lang(ja), :lang(ko) {{
  --measure-prose: var(--measure-cjk);
  line-height: 1.75;
}}
:lang(zh) h1, :lang(zh) h2, :lang(ja) h1, :lang(ja) h2, :lang(ko) h1, :lang(ko) h2 {{
  letter-spacing: 0;
  text-transform: none;
}}

/* Anti-AI-Slop Rule #4: Heading Proximity (margin-top = 1.8x to 2.5x margin-bottom) */
h2, h3 {{
  font-family: var(--font-heading);
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin-top: 2.2em;
  margin-bottom: 1em;
}}

/* Anti-AI-Slop Rule #5: 12-Column Asymmetrical Engineering Grid */
.b2b-asym-grid {{
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: clamp(1.25rem, 2.5vw, 2.5rem);
}}

/* Vercel Guideline: Tabular Numerals on B2B Spec Tables & Calculators */
table, .spec-table, .container-readout, .moq-badge {{
  font-variant-numeric: tabular-nums;
}}

/* Anti-AI-Slop Rule #2: Hairline 1px Borders Instead of Heavy Shadow Cards */
.b2b-spec-card {{
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  box-shadow: none;
}}
"""


def build_b2b_jsonld_tsx():
    """Generates src/components/seo/B2bJsonLd.tsx for same-source Organization + WebSite + WebPage + Product + FAQPage JSON-LD."""
    return """import React from 'react';

export interface B2bSpecProperty {
  kbId?: string;
  name: string;
  value: string;
  conditions?: string;
}

export interface B2bFaqItem {
  question: string;
  answer: string;
}

export interface B2bJsonLdProps {
  companyName: string;
  companyUrl: string;
  pageUrl: string;
  pageTitle: string;
  pageDescription: string;
  inLanguage?: string;
  logoUrl?: string;
  sameAs?: string[];
  productName?: string;
  productSku?: string;
  productDescription?: string;
  material?: string;
  specs?: B2bSpecProperty[];
  faqs?: B2bFaqItem[];
}

export function B2bJsonLd({
  companyName,
  companyUrl,
  pageUrl,
  pageTitle,
  pageDescription,
  inLanguage = 'en',
  logoUrl,
  sameAs = [],
  productName,
  productSku,
  productDescription,
  material,
  specs = [],
  faqs = [],
}: B2bJsonLdProps) {
  const graph: Record<string, unknown>[] = [
    {
      '@type': 'Organization',
      '@id': `${companyUrl}#organization`,
      name: companyName,
      url: companyUrl,
      ...(logoUrl ? { logo: logoUrl } : {}),
      ...(sameAs.length > 0 ? { sameAs } : {}),
    },
    {
      '@type': 'WebSite',
      '@id': `${companyUrl}#website`,
      url: companyUrl,
      name: companyName,
      publisher: { '@id': `${companyUrl}#organization` },
    },
    {
      '@type': 'WebPage',
      '@id': `${pageUrl}#webpage`,
      url: pageUrl,
      name: pageTitle,
      description: pageDescription,
      inLanguage,
      publisher: { '@type': 'Organization', name: companyName, url: companyUrl },
    },
  ];

  if (productName && productDescription) {
    graph.push({
      '@type': 'Product',
      '@id': `${pageUrl}#product`,
      name: productName,
      description: productDescription,
      ...(productSku ? { sku: productSku } : {}),
      ...(material ? { material } : {}),
      brand: { '@type': 'Brand', name: companyName },
      manufacturer: { '@id': `${companyUrl}#organization` },
      ...(specs.length > 0
        ? {
            additionalProperty: specs.map((s) => ({
              '@type': 'PropertyValue',
              name: s.name,
              value: s.value,
              ...(s.conditions ? { description: s.conditions } : {}),
            })),
          }
        : {}),
    });
  }

  if (faqs.length > 0) {
    graph.push({
      '@type': 'FAQPage',
      '@id': `${pageUrl}#faq`,
      mainEntity: faqs.map((f) => ({
        '@type': 'Question',
        name: f.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: f.answer,
        },
      })),
    });
  }

  const payload = {
    '@context': 'https://schema.org',
    '@graph': graph,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(payload) }}
    />
  );
}
"""


def build_keyword_tree(seed_keyword, industry_id, markets=None):
    seed = seed_keyword.strip()
    if not seed:
        raise ValueError('seed_keyword must not be empty')
    profile = get_industry(industry_id)
    markets = [m.strip() for m in (markets or ['Global']) if m.strip()]
    now = datetime.now(timezone.utc).isoformat()
    branches = []
    for branch in B2B_INTENT_BRANCHES:
        queries = [f'{seed} {mod}' for mod in branch['modifiers']]
        branches.append({
            'branch_id': branch['branch_id'],
            'intent_label': branch['intent_label'],
            'buyer_stage': branch['buyer_stage'],
            'target_page_type': branch['target_page_type'],
            'target_clean_url': branch['target_clean_url'],
            'kb_modules_required': branch['kb_modules_required'],
            'primary_cta_tier': branch['primary_cta_tier'],
            'primary_keyword': queries[0],
            'secondary_keywords': queries[1:],
            'h1_contract': f'Must include "{queries[0]}" or verified industrial equivalent in H1 and first 100 words',
            'h2_contract': queries[1:3],
            'serp_weakness_evidence': {
                'top10_has_inner_pages': None,
                'top10_dr_under_30_count': None,
                'b2b_supplier_share_ge_60pct': None,
                'search_volume_verified': None,
                'status': 'UNVERIFIED_VOLUME_AND_SERP',
            },
            'required_industry_fields': profile['product_fields'][:4],
            'required_evidence': profile['evidence'][:3],
            'industry_rfq_fields': profile.get('rfq_fields', [])[:4],
            'verification_status': 'UNVERIFIED_VOLUME_AND_SERP',
            'gate_rule': 'Verify real SERP buyer intent, DR<30 weakness, and search volume before locking page TDK. Never fabricate volume or KD numbers.',
        })
    return {
        'seed_keyword': seed,
        'pillar_homepage_keyword': f'{seed} manufacturer',
        'industry_id': industry_id,
        'industry_name': profile['name'],
        'industry_blueprint': {
            'layout': profile.get('layout', 'engineering'),
            'buyers': profile.get('buyers', []),
            'decision_path': profile.get('decision_path', ''),
            'topic_cluster_seeds': profile.get('topic_clusters', []),
            'red_lines': profile.get('red_lines', []),
            'missing_data_fallback': profile.get('missing_data_fallback', ''),
        },
        'visual_archetype': get_visual_archetype(industry_id),
        'target_markets': markets,
        'supported_locales': ['en', 'es', 'pt', 'ja', 'de', 'fr'],
        'generated_at': now,
        'gefei_b2b_competitor_teardown': {
            'domain_to_keyword': 'Extract top organic landing pages and inquiry keywords from 3-5 overseas B2B niche manufacturers/importers.',
            'keyword_to_domain': 'Inspect live SERP top 10 for each branch; confirm at least 60% are B2B supplier/spec pages rather than B2C retail listings, and check for inner-page rankings or DR < 30 weak spots.',
            'multilingual_rule': 'Never machine-translate keywords across languages; re-research native industrial nomenclature (e.g., DIN/EN for DE, ASTM for US, JIS for JA) per target market.',
        },
        'excluded_b2c_modifiers': ['cheap single piece', 'diy home craft', 'retail coupon', 'free shipping 1 pc', 'used second hand', 'paywall subscription'],
        'branches': branches,
        'handoff_contract': {
            'phase_1_to_phase_2': 'marketingskills (page-cro & copywriting) MUST read docs/seo/keyword-matrix.json, obey industry red_lines, and preserve each URL H1/H2 keyword contract.',
            'phase_2_to_phase_3': 'renwork-web-design-master & site_compiler.py enforce src/styles/design-tokens.css, data-layout, and the 6 Anti-AI-Slop visual rules.',
            'phase_3_to_phase_4': 'claude-seo, geo-seo-claude & validate_site.py enforce public-facts.json claim_ids parity, the 10-item Dual Audit Checklist, Cloudflare edge protection, and IndexNow/GSC push.',
        },
    }


def build_topic_cluster(seed_keyword, industry_id, market='Global'):
    """Builds a B2B Hub-and-Spoke Topic Cluster & Internal Link Stitching Plan fused with assets/industries.json topic_clusters."""
    seed = seed_keyword.strip()
    if not seed:
        raise ValueError('seed_keyword must not be empty')
    profile = get_industry(industry_id)
    f0, f1, f2 = (profile['product_fields'] + ['Material Grade', 'Dimension Tolerance', 'Packaging Spec'])[:3]
    e0, e1 = (profile['evidence'] + ['Inspection Report', 'Material Certificate'])[:2]
    now = datetime.now(timezone.utc).isoformat()
    slug_base = re.sub(r'[^a-z0-9]+', '-', seed.lower()).strip('-') or 'b2b-product'

    hubs = [
        {
            'hub_id': 'HUB-CATEGORY',
            'page_type': 'Pillar Category Hub',
            'clean_url': '/products/',
            'compiler_slug': 'products',
            'target_intent': f'{seed} manufacturer & industrial specification catalog',
            'primary_cta_tier': 'Tier 3: Container Load & Tiered FOB Quote',
            'required_elements': [
                'Zero-Friction First-Viewport Interactive Spec/Material Filter & Sample Basket Workbench',
                f'134-167 word self-contained engineering overview of {seed} supply capabilities (bound to verified RW claim_ids)',
                f'Semantic HTML comparison table across {f0}, {f1}, and {f2} with font-variant-numeric: tabular-nums',
                'Faceted navigation guard: filter parameters canonicalize to /products/ unless promoted to static Clean URL',
            ],
        },
        {
            'hub_id': 'HUB-OEM',
            'page_type': 'OEM / ODM Customization Hub',
            'clean_url': '/oem-odm/',
            'compiler_slug': 'oem-odm',
            'target_intent': f'custom {seed} OEM/ODM factory & private label tooling',
            'primary_cta_tier': 'Tier 2: Custom BOM / Drawing & Sample RFQ',
            'required_elements': [
                'First-viewport Interactive BOM / Customization Configurator (Option A vs Option B)',
                'Asymmetrical 12-column 4-step DFM, tooling, and sample sign-off workflow',
                f'Verifiable quality control gates ({e0}, {e1}) and Intent-Driven PAA FAQ',
            ],
        },
    ]

    spokes = [
        {
            'spoke_id': 'SPOKE-01',
            'article_type': 'Material & Specification Trade-off Guide',
            'clean_url': f'/resources/{slug_base}-material-specification-guide/',
            'compiler_slug': f'resources/{slug_base}-material-specification-guide',
            'headline': f'How to Specify {seed.title()} for Bulk Procurement: {f0} vs {f1} Trade-offs',
            'buyer_question_answered': f'Which {f0} and {f1} grades prevent field failure and optimize BOM unit cost?',
            'internal_link_stitches': [
                {'target_url': '/products/', 'anchor_text': f'industrial {seed} specification catalog', 'placement': 'First 200 words (context bridge)'},
                {'target_url': '/oem-odm/', 'anchor_text': f'custom {seed} BOM allocation and sampling', 'placement': 'Comparison table footer CTA'},
            ],
            'primary_cta_tier': 'Tier 1: Side-by-Side Spec Sample Kit Request',
        },
        {
            'spoke_id': 'SPOKE-02',
            'article_type': 'Quality Inspection & Compliance Protocol',
            'clean_url': f'/resources/{slug_base}-quality-control-testing-checklist/',
            'compiler_slug': f'resources/{slug_base}-quality-control-testing-checklist',
            'headline': f'B2B Quality Control Checklist for Sourcing {seed.title()}: Verifying {e0} and Batch Traceability',
            'buyer_question_answered': f'How do overseas procurement teams verify {e0}, {e1}, and pre-shipment AQL standards?',
            'internal_link_stitches': [
                {'target_url': '/capabilities/', 'anchor_text': f'{profile["name"]} quality management and lab testing workflow', 'placement': 'Testing methodology section'},
                {'target_url': '/contact/#inquiry', 'anchor_text': 'request a sample batch inspection report and RFQ', 'placement': 'Closing engineering summary'},
            ],
            'primary_cta_tier': 'Tier 1: Datasheet & Standard Sample Request',
        },
        {
            'spoke_id': 'SPOKE-03',
            'article_type': 'OEM Tooling, Packaging & Container Loading Playbook',
            'clean_url': f'/resources/{slug_base}-packaging-container-loading-optimization/',
            'compiler_slug': f'resources/{slug_base}-packaging-container-loading-optimization',
            'headline': f'Optimizing 20GP/40HQ Container Loading and Export Packaging for Bulk {seed.title()} Orders',
            'buyer_question_answered': 'How do carton dimensions, palletization, and gross weight limits impact landed unit cost?',
            'internal_link_stitches': [
                {'target_url': '/products/', 'anchor_text': '20GP/40HQ container volume and weight load estimator', 'placement': 'Container calculation section'},
                {'target_url': '/oem-odm/', 'anchor_text': f'custom export packaging and private label {seed} production', 'placement': 'Packaging specification section'},
            ],
            'primary_cta_tier': 'Tier 3: Container Load & Tiered FOB Quote',
        },
        {
            'spoke_id': 'SPOKE-04',
            'article_type': 'Application Operating Conditions & Selection Note',
            'clean_url': f'/resources/{slug_base}-application-engineering-selection/',
            'compiler_slug': f'resources/{slug_base}-application-engineering-selection',
            'headline': f'Application Engineering Guide: Selecting {seed.title()} for {market} Commercial & Industrial Environments',
            'buyer_question_answered': f'What operating conditions dictate {f2} selection in {market} applications?',
            'internal_link_stitches': [
                {'target_url': '/capabilities/', 'anchor_text': f'industry application solutions for {seed}', 'placement': 'Use-case matrix section'},
                {'target_url': '/products/', 'anchor_text': f'compare {seed} model specifications', 'placement': 'Selection summary table'},
            ],
            'primary_cta_tier': 'Tier 2: Application Engineering Consultation',
        },
    ]

    return {
        'seed_keyword': seed,
        'industry_id': industry_id,
        'industry_topic_seeds': profile.get('topic_clusters', []),
        'market': market,
        'generated_at': now,
        'anti_ai_slop_writing_rules': [
            'Open every guide directly with a TL;DR engineering summary: constraints, BOM cost drivers, or procurement failure modes (Vercel writing-guidelines).',
            'Ban generic filler openings ("In today\'s fast-paced world...", "Look no further...", "easy", "simple", "world-class").',
            'Use non-breaking spaces (&nbsp; or white-space: nowrap) between numbers and units (e.g., 500&nbsp;pcs, 0.8&nbsp;mm, 40&nbsp;HQ) and font-variant-numeric: tabular-nums on all specification tables.',
            'Include at least one semantic HTML <table> with explicit units/conditions and one 134-167 word self-contained GEO answer block per article.',
            'Every spoke article must link to at least 1 Hub page (/products/ or /oem-odm/) and 1 conversion route (/contact/#inquiry) using descriptive technical anchor text.',
        ],
        'hubs': hubs,
        'spokes': spokes,
    }


def audit_b2b_sku_catalog(catalog_path, industry_id):
    """Audits a B2B product SKU catalog JSON (inspired by wiebekaai/ecommerce-skills + benjaminsehl/liquid-skills + vercel-labs/agent-skills)."""
    raw = json.loads(Path(catalog_path).read_text(encoding='utf-8'))
    items = raw if isinstance(raw, list) else raw.get('products', raw.get('skus', []))
    if not isinstance(items, list):
        raise ValueError('catalog JSON must be a list of SKU objects or contain a "products"/"skus" array')
    profile = get_industry(industry_id)
    required_fields = profile['product_fields'][:3]
    seen_titles = set()
    issues = []
    ready_count = 0

    for idx, sku in enumerate(items):
        if not isinstance(sku, dict):
            continue
        sku_id = str(sku.get('sku') or sku.get('id') or f'SKU-{idx+1}')
        title = str(sku.get('title') or sku.get('name') or '').strip()
        desc = str(sku.get('seo_description') or sku.get('description') or '').strip()
        specs = sku.get('specifications') or sku.get('specs') or {}
        alt = str(sku.get('image_alt') or sku.get('alt') or '').strip()
        url = str(sku.get('url') or sku.get('slug') or '').strip()

        sku_issues = []
        if not title:
            sku_issues.append('Missing product title/model name')
        elif title.lower() in seen_titles:
            sku_issues.append(f'Duplicate product title detected: "{title}"')
        else:
            seen_titles.add(title.lower())

        word_count = len(re.findall(r'\b\w+\b', desc))
        if word_count < 30:
            sku_issues.append(f'Thin or missing B2B SEO description ({word_count} words; target 134-167 word GEO summary or >= 45 words)')
        for phrase in AI_SLOP_PHRASES:
            if phrase in desc.lower():
                sku_issues.append(f'Contains banned AI-slop phrase: "{phrase}"')

        if not isinstance(specs, dict) or len(specs) < 2:
            sku_issues.append(f'Missing structured specification dictionary (recommend including: {", ".join(required_fields)})')
        if not alt:
            sku_issues.append('Missing descriptive image alt text (should state model + material + application)')
        if url.endswith('.html'):
            sku_issues.append(f'Product URL exposes .html suffix: "{url}" (violates Clean URL policy)')

        if sku_issues:
            issues.append({'sku_id': sku_id, 'title': title or None, 'issues': sku_issues})
        else:
            ready_count += 1

    return {
        'catalog_file': str(catalog_path),
        'industry_id': industry_id,
        'total_skus': len(items),
        'seo_geo_ready_skus': ready_count,
        'skus_needing_fixes': len(issues),
        'recommended_industry_spec_columns': profile['product_fields'],
        'findings': issues,
    }


def build_b2b_syndication_pack(company, seed_keyword, industry_id, target_url='/products/'):
    """Generates platform-native B2B editorial distribution packs for LinkedIn, Medium, and YouTube (inspired by flaqai/backlink_skills + geo-seo-claude)."""
    profile = get_industry(industry_id)
    f0, f1, f2 = (profile['product_fields'] + ['Material Grade', 'Tolerance', 'Packaging'])[:3]
    e0, e1 = (profile['evidence'] + ['ISO 9001', 'Batch Test Report'])[:2]
    now = datetime.now(timezone.utc).isoformat()
    return {
        'company': company,
        'seed_keyword': seed_keyword,
        'industry_id': industry_id,
        'target_hub_clean_url': target_url,
        'generated_at': now,
        'channels': {
            'linkedin_technical_article': {
                'target_audience': 'Overseas Procurement Directors, Sourcing VPs, and OEM Product Managers',
                'headline_options': [
                    f'Engineering Trade-offs in Bulk {seed_keyword.title()} Sourcing: {f0} vs {f1}',
                    f'How B2B Buyers Verify {e0} and Prevent BOM Cost Overruns When Ordering {seed_keyword.title()}',
                ],
                'editorial_structure': [
                    '1. Field Failure / Cost Driver Hook (no generic AI intro)',
                    f'2. Specification Comparison Table ({f0}, {f1}, {f2})',
                    f'3. Factory QC & Pre-Shipment Verification ({e0}, {e1})',
                    f'4. Contextual Link to {target_url} and Sample Kit / Container Calculator CTA',
                ],
                'geo_brand_mention_rule': f'Explicitly associate "{company}" with "{seed_keyword} OEM/ODM manufacturing" and consistent technical terminology.',
            },
            'medium_engineering_publication': {
                'target_audience': 'Industrial Designers, Product Engineers, and Supply Chain Analysts',
                'headline_options': [
                    f'A Procurement Engineer\'s Guide to Specifying {seed_keyword.title()} ({f0}, Tolerances & 40HQ Logistics)',
                ],
                'canonical_and_link_rule': f'Use distinct editorial prose (never copy-paste website HTML verbatim); link descriptive anchor text to {target_url} and /contact/#inquiry.',
            },
            'youtube_factory_qc_transcript': {
                'target_audience': 'AI Search Retrieval Engines (Perplexity / Google AIO / ChatGPT) & Video-First B2B Buyers',
                'video_title': f'Inside {company}: {seed_keyword.title()} Manufacturing Process, {f0} Inspection & 40HQ Export Packaging',
                'description_and_transcript_requirements': [
                    f'Include a 150-word technical summary in the video description mentioning {company}, {seed_keyword}, {f0}, and {e0}.',
                    'Upload full human-verified closed captions (.srt) containing exact model numbers and testing standards so AI engines index the brand mention.',
                ],
            },
        },
    }


def init_b2b_seo_workspace(project_dir, company, seed_keyword, industry_id, markets=None):
    """Initializes the 4-Phase Collaborative Workspace deeply fused with cnproduct/b2b-global-brand-site-master."""
    project_path = Path(project_dir)
    seo_dir = project_path / 'docs/seo'
    claude_dir = project_path / '.claude'
    public_dir = project_path / 'public'
    styles_dir = project_path / 'src/styles'
    components_seo_dir = project_path / 'src/components/seo'
    for d in (seo_dir, claude_dir, public_dir, styles_dir, components_seo_dir):
        d.mkdir(parents=True, exist_ok=True)

    profile = get_industry(industry_id)
    archetype = get_visual_archetype(industry_id)
    maturity = assess_project_maturity(project_path)
    markets_list = [m.strip() for m in (markets or ['Global']) if m.strip()]
    now = datetime.now(timezone.utc).isoformat()

    # 1. docs/seo/keyword-matrix.json
    kw_matrix = build_keyword_tree(seed_keyword, industry_id, markets_list)
    (seo_dir / 'keyword-matrix.json').write_text(json.dumps(kw_matrix, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 2. docs/seo/topic-cluster.json
    cluster = build_topic_cluster(seed_keyword, industry_id, markets_list[0])
    (seo_dir / 'topic-cluster.json').write_text(json.dumps(cluster, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 3. docs/seo/syndication-pack.json
    syndication = build_b2b_syndication_pack(company, seed_keyword, industry_id, '/products/')
    (seo_dir / 'syndication-pack.json').write_text(json.dumps(syndication, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 4. src/styles/design-tokens.css & src/components/seo/B2bJsonLd.tsx
    (styles_dir / 'design-tokens.css').write_text(build_design_tokens_css(industry_id), encoding='utf-8')
    (components_seo_dir / 'B2bJsonLd.tsx').write_text(build_b2b_jsonld_tsx(), encoding='utf-8')

    # 5. docs/seo/site-brief.md (Deeply fused with industry.json 9 fields + M0/M1/M2 maturity + 21-module RenWork V4 KB)
    f_list = ', '.join(profile['product_fields'])
    e_list = ', '.join(profile['evidence'])
    rfq_list = ', '.join(profile.get('rfq_fields', []))
    buyers_list = ', '.join(profile.get('buyers', []))
    red_lines_md = '\n'.join(f'- 🛑 {r}' for r in profile.get('red_lines', []))
    brief_md = f"""# B2B Independent Site Brief (Single Source of Truth · V4.0)

- **Company Name**: {company}
- **Industry Blueprint**: `{industry_id}` ({profile['name']})
- **Compiler DOM Layout (`data-layout`)**: `{profile.get('layout', 'engineering')}`
- **Visual Archetype**: `{archetype['archetype_id']}` ({archetype['palette_direction']})
- **Typography Pairing**: {archetype['typography_pairing']}
- **Current Data Maturity Stage**: **{maturity['maturity_stage']}** — {maturity['summary']}
- **Primary Seed Keyword**: `{seed_keyword}`
- **Pillar Homepage Keyword**: `{seed_keyword} manufacturer`
- **Target Export Markets**: {', '.join(markets_list)}
- **Generated At**: {now}

## 1. Industry Procurement Blueprint (From `assets/industries.json`)
- **Target B2B Buyers (`buyers`)**: {buyers_list}
- **Buyer Decision Sequence (`decision_path`)**: `{profile.get('decision_path', '')}`
- **Mandatory Product Comparison Columns (`product_fields`)**: {f_list}
- **Required Trust & Verification Evidence (`evidence`)**: {e_list}
- **Progressive Industry RFQ Fields (`rfq_fields`)**: {rfq_list}
- **Missing-Data Fallback Strategy (`missing_data_fallback`)**: {profile.get('missing_data_fallback', '')}

## 2. Industry Red Lines (`red_lines` — Strictly Prohibited Unverified Claims)
{red_lines_md}

## 3. RenWork V4 21-Module Fact & Asset Boundary Guardrails
- Every quantitative claim, specification row, certificate, or factory metric must trace to a verified atomic knowledge card (`RW-XXXXXX-XXXX`) in `private/knowledge-cards.json` exported via `sitekit.py export` to `content/public-facts.json`.
- Every public image or PDF must be registered in `private/asset-register.json` with verified `sha256`, `rights_status`, and boolean `is_ai_generated`. AI-generated illustrations must never impersonate certificates, test reports, factory photos, or customer cases.
"""
    (seo_dir / 'site-brief.md').write_text(brief_md, encoding='utf-8')

    # 6. docs/seo/cro-copy-deck.md
    cro_md = f"""# B2B Landing Page CRO, Interactive Workbench & Copywriting Deck (V4.0)

> **Strict Alignment Rule**: Every H1 and H2 below MUST preserve the target keyword assigned in `docs/seo/keyword-matrix.json` (including in the Clean URL slug, `<title>`, `<h1>`, and first 100 words). Obey the industry `decision_path` (`{profile.get('decision_path', '')}`) and never violate `red_lines`.

## 1. First-Viewport Interactive B2B Workbench (`Zero-Signup Friction` Hero)
- **H1 Formula**: `[Verified {seed_keyword.title()} Supply / Manufacturing] for [{buyers_list}]`
- **Subheadline (constrained to `<= 65ch` Latin / `<= 36em` CJK)**: Highlight verifiable engineering parameters ({', '.join(profile['product_fields'][:4])}), batch quality control, and direct response without middleman markups.
- **Direct Action Workbench (Above the Fold)**: Embed a 1-click Material/Spec Preset Switcher or Mini 20GP/40HQ Carton Load Estimator (`sourcing_estimator.js`) directly in the first viewport. Product CTAs pass context via `/contact/?product=<Model>#inquiry`.

## 2. Asymmetrical 12-Column 4-Step B2B OEM / Sourcing Workflow (`data-layout="{profile.get('layout', 'engineering')}"`)
Render using a 12-column asymmetrical split (4-col sticky engineering header on left + 8-col structured steps on right):
1. **Spec & BOM Alignment**: Share target parameters ({', '.join(profile.get('rfq_fields', [])[:3])}) or reference sample specs.
2. **Engineering DFM & Prototype Sampling**: Confirm pre-production sample and lab test criteria ({', '.join(profile['evidence'][:3])}).
3. **In-Line QC & Pre-Shipment Inspection**: Batch traceability and AQL inspection prior to container sealing.
4. **Export Packaging & Global Logistics**: Palletized or floor-loaded 20GP/40HQ shipment with full customs documentation.

## 3. B2B Risk Reversal & 3-Tier Commercial Inquiry Matrix (Replaces SaaS Paywalls)
Never place paywalls on B2B specifications. Use a 3-Tier Commercial Inquiry Matrix paired with progressive `email_draft` (default) or `http` (`rfq_daemon.py` with HMAC math captcha & honeypot):

| Tier | Target Buyer Stage | Commercial Scope | Risk Reversal Micro-Copy | Primary Action |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Standard Sample & Spec Pack** | Engineering Evaluation | Existing tooling models & material swatches | Strict NDA protection; courier freight credit on first bulk order | `Request Standard Sample Pack` |
| **Tier 2: Custom OEM / ODM Project** | Private Label / Custom Spec | Custom material allocation, logo tooling, bespoke packaging | Golden sample sign-off before mass production; documented QC gates | `Submit Custom BOM / Drawing RFQ` |
| **Tier 3: Bulk Container Procurement** | Repeat Wholesale / 20GP-40HQ | Mixed-SKU container loading & tiered FOB volume pricing | Pre-shipment third-party inspection support (SGS/Intertek/BV) | `Calculate Container Load & Get FOB Quote` |

## 4. Intent-Driven Procurement FAQ (5-8 Real Buyer PAA Questions)
Answer concrete buyer questions regarding MOQ mixing across SKUs, mold/tooling ownership, sample lead times, pre-shipment AQL standards, and payment/incoterms (`FOB`, `CIF`, `DDP`), feeding `src/components/seo/B2bJsonLd.tsx`.
"""
    (seo_dir / 'cro-copy-deck.md').write_text(cro_md, encoding='utf-8')

    # 7. docs/seo/backlink-tracker.csv
    csv_buf = io.StringIO()
    writer = csv.writer(csv_buf)
    writer.writerow(['target_id', 'domain', 'submit_url', 'track', 'gate_type', 'state', 'live_url', 'rel_attribute', 'dr_estimate', 'updated_at', 'notes'])
    writer.writerow(['BL-0001', 'example-b2b-directory.com', 'https://example-b2b-directory.com/submit', 'batch_directory', 'open-form', 'candidate', '', '', '', now, 'Verify live URL and rel attribute before marking rel_verified'])
    writer.writerow(['BL-0002', 'linkedin.com', 'https://www.linkedin.com/articles/', 'editorial_authority', 'account', 'candidate', '', '', '98', now, 'Publish B2B material trade-off engineering guide linking to /products/'])
    writer.writerow(['BL-0003', 'youtube.com', 'https://www.youtube.com/', 'brand_mention_surface', 'account', 'candidate', '', '', '99', now, 'Upload factory QC & production line video with full technical transcript'])
    (seo_dir / 'backlink-tracker.csv').write_text(csv_buf.getvalue(), encoding='utf-8')

    # 8. docs/seo/status-log.md
    status_md = f"""# B2B Site SEO / GEO Lifecycle & 10-Item Dual Audit Log (V4.0)

- **Project**: {company} (`{industry_id}`)
- **Data Maturity Stage**: **{maturity['maturity_stage']}** ({maturity['verified_public_fact_cards']} verified public facts, {maturity['approved_public_assets']} approved public assets)
- **Compiler DOM Layout**: `data-layout="{profile.get('layout', 'engineering')}"`
- **Visual Archetype**: `{archetype['archetype_id']}`
- **Initialized At**: {now}

## Pre-Release 10-Item Dual Audit Checklist (SEO/GEO + Zero AI-Slop Visual + Fact/Edge Governance)

1. [ ] **Keyword & Intent Alignment**: Primary keyword is present in Clean URL slug, `<title>`, `<h1>`, and first 100 words; SERP B2B supplier intent >= 60%.
2. [ ] **RenWork V4 Fact & Asset Parity**: All specs trace to `content/public-facts.json` (`claim_ids`); all media verified in `private/asset-register.json` (no AI images impersonating certificates/factories).
3. [ ] **Zero-Friction First-Viewport Workbench**: First viewport includes an interactive spec filter, swatch switcher, or 20GP/40HQ container calculator plus `/contact/?product=...#inquiry` context passing.
4. [ ] **Zero Neon Gradient Gimmicks**: No `bg-clip-text text-transparent bg-gradient-to-r` highlights on headline words.
5. [ ] **Multi-Script Measure & Tabular Numerals**: Paragraphs constrained to `65ch` (Latin) / `36em` (CJK); all spec tables enforce `font-variant-numeric: tabular-nums` and `&nbsp;` between numbers and units; tested at `320/390/768/1440px` and `200%` zoom.
6. [ ] **Heading Proximity & Card Discipline**: H2/H3 `margin-top` is `1.8x-2.5x` `margin-bottom`; zero `shadow-xl` cards or pure hex greys (`#777/#888/#999`); button contrast >= 4.5:1 (`extract_brand_dna.py`).
7. [ ] **12-Column Asymmetrical Grid & `data-layout`**: Uses `data-layout="{profile.get('layout', 'engineering')}"` and 12-column asymmetrical splits rather than monotonous centered cards.
8. [ ] **Same-Source B2B JSON-LD**: `WebPage` + `Organization` + `Product` (+ optional `FAQPage`) match visible HTML metadata and canonical URLs with zero fabricated prices or ratings (`validate_site.py`).
9. [ ] **GEO Citability >= 85 & `llms.txt` Parity**: Core pages contain a 134-167 word self-contained engineering answer block, semantic `<table>` specs, and synced `/public/llms.txt` + `/public/llms-full.txt`.
10. [ ] **Clean URLs, Anti-FOUC, Edge Protection & IndexNow**: Zero `.html` suffixes, SHA-256 CSS/JS cache-busting (`?v={hash}`), Cloudflare Workers edge protection bundle (`private/deploy/edge-*/` with `READ_LIMITER=300/60s`, `INQUIRY_LIMITER=5/60s`, `verifiedBot` exemption, anti-iframe `X-Frame-Options: DENY`), and IndexNow/GSC submission.
"""
    (seo_dir / 'status-log.md').write_text(status_md, encoding='utf-8')

    # 9. public/llms.txt & public/llms-full.txt
    llms_txt = f"""# {company}

> B2B {profile['name']} supply and OEM/ODM technical portal for {seed_keyword}. All specifications and commercial terms are governed by verified public fact cards.

## Core Procurement Pages
- [Home & Capabilities](/): Overview of {company} scope
- [Product Specification Catalog](/products/): Technical parameters ({', '.join(profile['product_fields'][:4])}) and model comparisons
- [Capabilities & Quality](/capabilities/): Testing standards ({', '.join(profile['evidence'][:3])}) and batch traceability
- [OEM / ODM Customization](/oem-odm/): Custom BOM, tooling, sampling, and private label workflow
- [Technical Resources](/resources/): Engineering selection guides and container loading optimization
- [Request a Quote (RFQ)](/contact/#inquiry): Direct engineering inquiry and multi-SKU sample request
"""
    (public_dir / 'llms.txt').write_text(llms_txt, encoding='utf-8')

    llms_full_txt = llms_txt + f"""
## Technical Procurement Reference Summary
- **Industry**: {profile['name']} (`{industry_id}`)
- **Buyer Personas**: {buyers_list}
- **Decision Path**: {profile.get('decision_path', '')}
- **Core Specification Dimensions**: {f_list}
- **Standard Verification Evidence**: {e_list}
- **Progressive RFQ Fields**: {rfq_list}
- **Note**: Only verified facts exported in `content/public-facts.json` constitute binding company claims.
"""
    (public_dir / 'llms-full.txt').write_text(llms_full_txt, encoding='utf-8')

    # 10. .claude/CLAUDE.md
    claude_md = f"""# B2B Export Independent Site - Skill Orchestration Protocol (`.claude/CLAUDE.md` · V4.0)

This project runs the **`b2b-seo-geo-site-master` V4.0** unified workflow, deeply fusing all 12 engineering subsystems of `cnproduct/b2b-global-brand-site-master` with 13 open-source SEO, GEO, CRO, and UI/UX skills.
All SEO, GEO, and CRO planning context MUST read and write through **`docs/seo/`**, while all company claims and assets are strictly governed by **`private/knowledge-cards.json` -> `content/public-facts.json`** and **`private/asset-register.json`**.

## 1. Strict 4-Phase Skill Routing Rules

1. **Phase 1: Fact Ingestion (`M0/M1/M2`), Keyword Matrix & SERP Teardown (`orchestrator.py` + `sitekit.py` + `seo_geo_matrix.py`)**
   - **Single Source of Truth**: `private/knowledge-cards.json` (RenWork V4 7 states, 00-20 modules), `private/gaps.md`, `docs/seo/keyword-matrix.json`, `docs/seo/topic-cluster.json`, and `docs/seo/site-brief.md`.
   - **Mandatory Rule**: Assess data maturity (`M0` / `M1` / `M2`), obey industry `red_lines`, verify SERP B2B supplier intent (>= 60%), and ensure the primary keyword appears in the Clean URL slug, `<title>`, `<h1>`, and first 100 words.

2. **Phase 2: First-Viewport B2B Workbench, 10 Page Blueprints & Dual-Mode RFQ (`marketingskills` + `liquid-skills` + `rfq_daemon.py`)**
   - **Single Source of Truth**: `docs/seo/cro-copy-deck.md`, `content/site.json`, and `content/public-facts.json`.
   - **Mandatory Rule**: Follow the industry's `decision_path` (`{profile.get('decision_path', '')}`). Place a **Zero-Signup Friction Interactive Workbench** in the first viewport, pass product context to `/contact/?product=<Model>#inquiry`, and use **3-Tier Commercial RFQ Cards** with B2B Risk Reversal (default `email_draft` mode, or approved `http` mode backed by `scripts/rfq_daemon.py`).

3. **Phase 3: Zero AI-Slop UI, Multi-Script Typography & `data-layout` (`extract_brand_dna.py` + `design_math.py` + `renwork-web-design-master`)**
   - **Single Source of Truth**: `src/styles/design-tokens.css`, `DESIGN.md`, and `private/brand-tokens.json`.
   - **Mandatory Rule**: Enforce the 6 Anti-AI-Slop Rules, WCAG >= 4.5:1 button contrast, `font-variant-numeric: tabular-nums` on spec tables, `&nbsp;` between numbers and units, Latin `65ch` / CJK `36em` / RTL `dir="rtl"` rules, and viewport verification across `320/390/768/1440px` and `200%` zoom.

4. **Phase 4: Compiler, 10-Item Dual Audit, Edge Protection Bundle & Indexing Closure (`site_compiler.py` + `validate_site.py` + `seo_geo_matrix.py`)**
   - **Single Source of Truth**: `builds/site-*/`, `private/deploy/edge-*/` (`worker.mjs` + `wrangler.json` + `policy.json`), `acceptance.md`, `docs/seo/status-log.md`, and `private/backlink-ledger.json`.
   - **Mandatory Rule**: Deploy only via the generated Cloudflare Workers `deployment_directory` bundle (`run_worker_first: true`, `READ_LIMITER=300/60s`, `INQUIRY_LIMITER=5/60s`, `verifiedBot` exemption, `X-Frame-Options: DENY`). Never upload the root project directory containing `private/`. Record de-identified lessons via `scripts/record_learning.py`.
"""
    (claude_dir / 'CLAUDE.md').write_text(claude_md, encoding='utf-8')

    return {
        'workspace_initialized': str(project_path),
        'maturity_stage': maturity['maturity_stage'],
        'visual_archetype': archetype['archetype_id'],
        'compiler_data_layout': profile.get('layout', 'engineering'),
        'files_created': [
            str(seo_dir / 'site-brief.md'),
            str(seo_dir / 'keyword-matrix.json'),
            str(seo_dir / 'topic-cluster.json'),
            str(seo_dir / 'syndication-pack.json'),
            str(seo_dir / 'cro-copy-deck.md'),
            str(seo_dir / 'backlink-tracker.csv'),
            str(seo_dir / 'status-log.md'),
            str(styles_dir / 'design-tokens.css'),
            str(components_seo_dir / 'B2bJsonLd.tsx'),
            str(public_dir / 'llms.txt'),
            str(public_dir / 'llms-full.txt'),
            str(claude_dir / 'CLAUDE.md'),
        ],
    }


class _HTMLCitabilityParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._stack = []
        self.paragraphs = []
        self._current_p = []
        self.table_count = 0
        self.th_count = 0
        self.h1_count = 0
        self.h2_h3_questions = 0
        self._current_heading = []
        self.has_json_ld = False
        self.links = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self._stack.append(tag)
        attr_dict = dict(attrs)
        if tag == 'p':
            self._current_p = []
        elif tag in ('h1', 'h2', 'h3'):
            self._current_heading = []
            if tag == 'h1':
                self.h1_count += 1
        elif tag == 'table':
            self.table_count += 1
        elif tag == 'th':
            self.th_count += 1
        elif tag == 'script' and attr_dict.get('type') == 'application/ld+json':
            self.has_json_ld = True
        elif tag == 'a' and attr_dict.get('href'):
            self.links.append(attr_dict['href'])

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'p':
            text = ' '.join(''.join(self._current_p).split())
            if text:
                self.paragraphs.append(text)
            self._current_p = []
        elif tag in ('h1', 'h2', 'h3'):
            htext = ' '.join(''.join(self._current_heading).split())
            if tag in ('h2', 'h3') and ('?' in htext or htext.lower().startswith(('how ', 'what ', 'which ', 'why ', 'when '))):
                self.h2_h3_questions += 1
            self._current_heading = []
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if not self._stack:
            return
        top = self._stack[-1]
        if top in ('script', 'style'):
            return
        if 'p' in self._stack:
            self._current_p.append(data)
        if any(h in self._stack for h in ('h1', 'h2', 'h3')):
            self._current_heading.append(data)


def score_geo_citability(file_path):
    """Scores a B2B HTML/JSX/Markdown file on the 0-100 B2B GEO Citability & Zero-AI-Slop Dual Audit Rubric (V4.0)."""
    raw = Path(file_path).read_text(encoding='utf-8')
    is_html = '<html' in raw.lower() or '<body' in raw.lower() or '<table' in raw.lower() or '<p>' in raw.lower()

    if is_html:
        parser = _HTMLCitabilityParser()
        parser.feed(raw)
        paragraphs = parser.paragraphs
        table_count = parser.table_count
        th_count = parser.th_count
        h1_count = parser.h1_count
        has_json_ld = parser.has_json_ld
        links = parser.links
    else:
        blocks = [b.strip() for b in re.split(r'\n\s*\n', raw) if b.strip()]
        paragraphs = [b for b in blocks if not b.startswith(('#', '|', '-', '*', '```'))]
        table_count = sum(1 for b in blocks if '|' in b and '---' in b)
        th_count = table_count * 3
        h1_count = sum(1 for line in raw.splitlines() if line.startswith('# '))
        has_json_ld = 'application/ld+json' in raw or 'B2bJsonLd' in raw
        links = re.findall(r'\]\(([^)]+)\)', raw)

    word_counts = [len(re.findall(r'\b\w+\b', p)) for p in paragraphs]
    optimal_passages = [wc for wc in word_counts if 120 <= wc <= 180]
    near_optimal_passages = [wc for wc in word_counts if 80 <= wc < 120 or 180 < wc <= 220]

    if optimal_passages:
        passage_score = 25
    elif near_optimal_passages:
        passage_score = 18
    elif any(wc >= 40 for wc in word_counts):
        passage_score = 10
    else:
        passage_score = 0

    unit_matches = re.findall(r'\b\d+(?:\.\d+)?\s*(?:mm|cm|m|kg|g|ml|l|pcs|cbm|20gp|40hq|mpa|kw|v|hz|%|°c|iso|astm|din|ce|fsc)\b', raw.lower())
    spec_score = 0
    if table_count >= 1 and th_count >= 2:
        spec_score += 15
    if len(unit_matches) >= 5:
        spec_score += 10
    elif len(unit_matches) >= 2:
        spec_score += 5

    slop_hits = [phrase for phrase in AI_SLOP_PHRASES if phrase in raw.lower()]
    ui_slop_hits = [label for token, label in UI_SLOP_PATTERNS if token in raw.lower()]
    eeat_score = max(0, 20 - (len(slop_hits) + len(ui_slop_hits)) * 5)

    tech_score = 0
    if h1_count == 1:
        tech_score += 5
    html_link_violations = [lk for lk in links if lk.endswith('.html') or '.html#' in lk]
    if not html_link_violations:
        tech_score += 5
    if has_json_ld or not is_html:
        tech_score += 5

    rfq_links = [lk for lk in links if any(k in lk.lower() for k in ('contact', 'rfq', 'inquiry', 'quote', 'sample', 'calculator', 'oem'))]
    funnel_score = 15 if rfq_links else (8 if ('rfq' in raw.lower() or 'inquiry' in raw.lower() or 'sample' in raw.lower()) else 0)

    total = passage_score + spec_score + eeat_score + tech_score + funnel_score
    findings = []
    if not optimal_passages:
        findings.append({
            'finding': 'No self-contained 134-167 word GEO engineering answer block detected',
            'evidence': f'Paragraph word counts: {word_counts[:8]}',
            'impact': 'AI search engines (ChatGPT, Perplexity, Google AIO) prefer self-contained 134-167 word factual passages for direct grounding citations.',
            'fix': 'Add a 134-167 word engineering summary paragraph immediately below the H1/intro that states application scope, material grades, tolerances, and testing conditions.',
            'severity': 'Warning',
            'confidence': 'Confirmed',
        })
    if table_count == 0:
        findings.append({
            'finding': 'Missing semantic specification or comparison table',
            'evidence': 'table_count = 0',
            'impact': 'B2B buyers and LLM retrieval agents rely on structured <table> data to compare models, materials, and MOQ/container specs.',
            'fix': 'Insert a semantic HTML <table> with <thead>, <th scope="col">, and font-variant-numeric: tabular-nums listing verified model parameters, units, and test conditions.',
            'severity': 'Warning',
            'confidence': 'Confirmed',
        })
    if html_link_violations:
        findings.append({
            'finding': 'Internal links expose .html extensions (Clean URL violation)',
            'evidence': f'Links with .html: {html_link_violations[:5]}',
            'impact': 'Splits canonical authority and violates the Clean URL policy.',
            'fix': 'Strip .html suffixes from all href, canonical, og:url, JSON-LD, and sitemap URLs.',
            'severity': 'Critical',
            'confidence': 'Confirmed',
        })
    if slop_hits or ui_slop_hits:
        findings.append({
            'finding': 'AI-slop prose clichés or banned UI patterns detected (10-Item Dual Audit violation)',
            'evidence': f'Prose clichés: {slop_hits}; UI violations: {ui_slop_hits}',
            'impact': 'Erodes B2B engineering credibility, E-E-A-T Trust score, and visual brand authority.',
            'fix': 'Remove neon text gradients, shadow-xl cards, pure hex greys (#777/#888/#999), and generic adjectives; apply src/styles/design-tokens.css.',
            'severity': 'Warning',
            'confidence': 'Confirmed',
        })

    return {
        'file': str(file_path),
        'composite_geo_score': total,
        'breakdown': {
            'passage_citability_25': passage_score,
            'semantic_spec_and_unit_density_25': spec_score,
            'anti_slop_prose_and_ui_discipline_20': eeat_score,
            'technical_clean_url_and_schema_15': tech_score,
            'b2b_rfq_funnel_stitching_15': funnel_score,
        },
        'metrics': {
            'paragraph_word_counts': word_counts,
            'optimal_120_180_word_passages': len(optimal_passages),
            'table_count': table_count,
            'quantitative_unit_mentions': len(unit_matches),
            'clean_url_violations': len(html_link_violations),
            'ui_slop_violations': len(ui_slop_hits),
        },
        'findings': findings,
    }


def build_geo_prompt_suite(company, seed_keyword, industry_id, market='Global'):
    company = company.strip()
    seed = seed_keyword.strip()
    if not company or not seed:
        raise ValueError('company and seed_keyword must not be empty')
    profile = get_industry(industry_id)
    fields = ', '.join(profile['product_fields'][:3])
    evidences = ', '.join(profile['evidence'][:2])
    now = datetime.now(timezone.utc).isoformat()
    prompts = [
        {
            'id': 'GEO-01',
            'category': 'non_brand_supplier_discovery',
            'prompt': f'Who are reliable OEM/ODM manufacturers for {seed} supplying {market} buyers, and what technical specifications should I verify before requesting samples?',
            'target_citation_page': '/oem-odm/',
        },
        {
            'id': 'GEO-02',
            'category': 'technical_spec_comparison',
            'prompt': f'Compare the key engineering and material options for {seed}, specifically evaluating {fields} for bulk B2B procurement.',
            'target_citation_page': '/products/',
        },
        {
            'id': 'GEO-03',
            'category': 'quality_and_compliance',
            'prompt': f'What quality control tests and documentation ({evidences}) are required when sourcing {seed} from an export manufacturer?',
            'target_citation_page': '/capabilities/',
        },
        {
            'id': 'GEO-04',
            'category': 'packaging_and_container_logistics',
            'prompt': f'How do B2B buyers estimate 20GP and 40HQ container loading capacity, carton dimensions, and lead time when ordering {seed} in bulk?',
            'target_citation_page': '/products/',
        },
        {
            'id': 'GEO-05',
            'category': 'brand_entity_verification',
            'prompt': f'What products, technical capabilities, and OEM customization services does {company} provide for {seed} buyers?',
            'target_citation_page': '/',
        },
        {
            'id': 'GEO-06',
            'category': 'rfq_preparation_checklist',
            'prompt': f'What exact technical parameters and BOM details should a procurement engineer include in an RFQ for custom {seed}?',
            'target_citation_page': '/contact/#inquiry',
        },
    ]
    return {
        'company': company,
        'seed_keyword': seed,
        'industry_id': industry_id,
        'market': market,
        'generated_at': now,
        'offsite_brand_mention_surfaces': [
            'LinkedIn Company Page & Technical Articles (3x stronger AI citation correlation when paired with consistent entity naming)',
            'YouTube Factory Tour & QC Testing Video Transcripts',
            'Industry Trade Directories & Verified Exporter Registries (sameAs entity alignment)',
            'Medium / Technical Engineering Comparison Publications',
        ],
        'evaluation_protocol': {
            'engines': ['Google AI Overviews / AI Mode', 'ChatGPT Search (OAI-SearchBot)', 'Perplexity (PerplexityBot)', 'Bing Copilot'],
            'metrics': [
                'mention_rate',
                'linked_citation_rate',
                'cited_url_accuracy',
                'factual_claim_accuracy',
                'ai_referral_sessions',
                'qualified_rfq_conversions',
            ],
            'guardrail': 'Record engine, date, region, web-search toggle, and verbatim cited URLs. Small-sample prompt checks are observations, not global share guarantees.',
        },
        'prompts': prompts,
    }


def validate_backlink_entry(entry):
    required = ('target_id', 'domain', 'submit_url', 'track', 'gate_type', 'state', 'updated_at')
    if not isinstance(entry, dict):
        return 'entry must be a JSON object'
    for key in required:
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            return f'missing or empty {key}'
    if entry['track'] not in ('batch_directory', 'editorial_authority', 'brand_mention_surface'):
        return 'track must be batch_directory, editorial_authority, or brand_mention_surface'
    if entry['gate_type'] not in ('open-form', 'account', 'captcha-interactive', 'captcha-passive', 'reciprocal', 'personal-contact', 'email-verify'):
        return 'invalid gate_type'
    state = entry['state']
    if state.startswith('indexed@'):
        engine = state.split('@', 1)[1].strip()
        if not engine:
            return 'indexed state must specify engine, e.g. indexed@google or indexed@bing'
    elif state not in BACKLINK_STATES or state == 'indexed':
        return 'state must be one of candidate/qualified/filled/submitted/public/indexed@<engine>/rel_verified'
    if state == 'rel_verified':
        if not isinstance(entry.get('live_url'), str) or not entry['live_url'].startswith(('http://', 'https://')):
            return 'rel_verified requires a verified live_url'
        if entry.get('rel_attribute') not in ('dofollow', 'nofollow', 'ugc', 'sponsored', 'redirect_wrapped', 'brand_mention_unlinked'):
            return 'rel_verified requires audited rel_attribute'
    return None


def init_backlink_ledger(output_path):
    now = datetime.now(timezone.utc).isoformat()
    sample = {
        'schema_version': '1.1.0',
        'updated_at': now,
        'rules': [
            'Never count a submitted directory form as an active backlink until live_url, HTTP status, redirect chain, and rel attribute are verified.',
            'Indexed status must specify the search engine explicitly (e.g., indexed@google, indexed@bing).',
            'Never bypass CAPTCHA, 2FA, or forced reciprocal link gates automatically; queue interactive verification for human approval.',
            'Track off-site B2B brand mentions (LinkedIn technical articles, YouTube QC transcripts, trade registries) under track=brand_mention_surface for GEO authority.',
        ],
        'entries': [
            {
                'target_id': 'BL-0001',
                'domain': 'example-b2b-directory.com',
                'submit_url': 'https://example-b2b-directory.com/submit',
                'track': 'batch_directory',
                'gate_type': 'open-form',
                'state': 'candidate',
                'live_url': None,
                'rel_attribute': None,
                'updated_at': now,
                'notes': 'Template candidate entry; replace with verified B2B industry directories, trade publications, or brand mention surfaces.',
            }
        ],
    }
    Path(output_path).write_text(json.dumps(sample, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return sample


def validate_ledger_file(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    entries = data.get('entries')
    if not isinstance(entries, list):
        raise ValueError('entries must be a list')
    seen = set()
    for idx, item in enumerate(entries):
        err = validate_backlink_entry(item)
        if err:
            raise ValueError(f'entry[{idx}]: {err}')
        tid = item['target_id']
        if tid in seen:
            raise ValueError(f'duplicate target_id: {tid}')
        seen.add(tid)
    return {'valid': True, 'count': len(entries)}


def self_test():
    tree = build_keyword_tree('stainless steel bento box', 'bento', ['US', 'EU'])
    assert len(tree['branches']) == 6
    assert 'red_lines' in tree['industry_blueprint']
    assert tree['visual_archetype']['compiler_data_layout'] == 'oem'
    stone_tree = build_keyword_tree('tumbled limestone pavers', 'limestone', ['US', 'UK', 'AU'])
    assert stone_tree['visual_archetype']['archetype_id'] == 'architectural_material'
    assert stone_tree['visual_archetype']['compiler_data_layout'] == 'materials'
    with tempfile.TemporaryDirectory() as tmp:
        ws = init_b2b_seo_workspace(tmp, 'Example Bento Co.', 'stainless steel bento box', 'bento', ['US', 'DE'])
        assert len(ws['files_created']) == 12
        assert ws['maturity_stage'] == 'M0'
        assert (Path(tmp) / 'src/styles/design-tokens.css').is_file()
        assert (Path(tmp) / 'src/components/seo/B2bJsonLd.tsx').is_file()
        ledger_path = Path(tmp) / 'private/backlink-ledger.json'
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        init_backlink_ledger(ledger_path)
        assert validate_ledger_file(ledger_path)['valid'] is True
        cit = score_geo_citability(Path(tmp) / 'docs/seo/cro-copy-deck.md')
        assert 'composite_geo_score' in cit
    print('PASS: seo_geo_matrix V4.0 (deep fusion with 22 industries, M0/M1/M2 maturity, RenWork V4 21-module binding, design-tokens.css, B2bJsonLd.tsx, citability-score & 7-state backlink ledger)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('self-test')

    iw = sub.add_parser('init-workspace', help='Initialize 4-Phase B2B SEO/GEO/CRO Single Source of Truth hub')
    iw.add_argument('--project', required=True)
    iw.add_argument('--company', required=True)
    iw.add_argument('--seed', required=True)
    iw.add_argument('--industry', required=True)
    iw.add_argument('--markets', default='Global')

    kt = sub.add_parser('keyword-tree', help='Generate 6-branch B2B commercial intent keyword tree + industry blueprint + H1/H2 contract')
    kt.add_argument('--seed', required=True)
    kt.add_argument('--industry', required=True)
    kt.add_argument('--markets', default='Global')
    kt.add_argument('--out')

    tc = sub.add_parser('topic-cluster', help='Generate B2B Hub-and-Spoke topic cluster & internal link stitching plan')
    tc.add_argument('--seed', required=True)
    tc.add_argument('--industry', required=True)
    tc.add_argument('--market', default='Global')
    tc.add_argument('--out')

    cs = sub.add_parser('citability-score', help='Score an HTML/JSX/Markdown file on the 0-100 B2B GEO Citability & Zero-AI-Slop Dual Audit Rubric')
    cs.add_argument('--file', required=True)
    cs.add_argument('--out')

    ca = sub.add_parser('catalog-audit', help='Audit a B2B SKU catalog JSON for missing specs, thin SEO descriptions, and Clean URL compliance')
    ca.add_argument('--file', required=True)
    ca.add_argument('--industry', required=True)
    ca.add_argument('--out')

    sp = sub.add_parser('syndication-pack', help='Generate B2B LinkedIn, Medium, and YouTube transcript syndication packs')
    sp.add_argument('--company', required=True)
    sp.add_argument('--seed', required=True)
    sp.add_argument('--industry', required=True)
    sp.add_argument('--url', default='/products/')
    sp.add_argument('--out')

    gp = sub.add_parser('geo-prompts', help='Generate B2B GEO buyer prompt benchmark suite & off-site brand mention plan')
    gp.add_argument('--company', required=True)
    gp.add_argument('--seed', required=True)
    gp.add_argument('--industry', required=True)
    gp.add_argument('--market', default='Global')
    gp.add_argument('--out')

    bl_init = sub.add_parser('init-ledger', help='Initialize 7-state B2B backlink & brand mention evidence ledger')
    bl_init.add_argument('--out', required=True)

    bl_val = sub.add_parser('validate-ledger', help='Validate 7-state B2B backlink & brand mention evidence ledger')
    bl_val.add_argument('--file', required=True)

    args = parser.parse_args()
    try:
        if args.command == 'self-test':
            self_test()
        elif args.command == 'init-workspace':
            markets = [m.strip() for m in args.markets.split(',') if m.strip()]
            result = init_b2b_seo_workspace(args.project, args.company, args.seed, args.industry, markets)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.command == 'keyword-tree':
            markets = [m.strip() for m in args.markets.split(',') if m.strip()]
            result = build_keyword_tree(args.seed, args.industry, markets)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'topic-cluster':
            result = build_topic_cluster(args.seed, args.industry, args.market)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'citability-score':
            result = score_geo_citability(args.file)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'catalog-audit':
            result = audit_b2b_sku_catalog(args.file, args.industry)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'syndication-pack':
            result = build_b2b_syndication_pack(args.company, args.seed, args.industry, args.url)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'geo-prompts':
            result = build_geo_prompt_suite(args.company, args.seed, args.industry, args.market)
            output = json.dumps(result, ensure_ascii=False, indent=2)
            if args.out:
                Path(args.out).write_text(output + '\n', encoding='utf-8')
            print(output)
        elif args.command == 'init-ledger':
            result = init_backlink_ledger(args.out)
            print(json.dumps({'created': args.out, 'entries': len(result['entries'])}, ensure_ascii=False))
        elif args.command == 'validate-ledger':
            print(json.dumps(validate_ledger_file(args.file), ensure_ascii=False))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as err:
        print('ERROR: ' + str(err), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
