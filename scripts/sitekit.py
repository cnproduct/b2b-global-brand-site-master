#!/usr/bin/env python3
"""Local project bootstrap and fail-closed public fact projection; Python stdlib only."""
import argparse
import hashlib
import json
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_KEYS = ('kb_id', 'title', 'language', 'conclusion', 'conditions', 'updated_at')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def profiles():
    return read(ROOT / 'assets/industries.json')['industries']


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp needs timezone')
    return parsed


def eligibility(card, tenant, now):
    if not isinstance(card, dict):
        return 'card must be an object'
    if card.get('tenant_id') != tenant:
        return 'tenant mismatch'
    if card.get('knowledge_kind') != 'fact':
        return 'not a fact'
    if card.get('status') not in ('verified_fact', 'public_fact'):
        return 'unverified, conflicting or inactive status'
    if card.get('sensitivity') != 'public' or card.get('public_claim_approved') is not True:
        return 'not explicitly approved for public use'
    if not all(isinstance(card.get(k), str) for k in PUBLIC_KEYS):
        return 'invalid public field types'
    if not all(card[k].strip() for k in ('kb_id', 'title', 'language', 'conclusion', 'updated_at')):
        return 'empty public field'
    if not re.fullmatch(r'RW-[A-Z0-9]{6}-[0-9]{4,6}', card['kb_id']):
        return 'invalid knowledge ID'
    try:
        updated = timestamp(card['updated_at'])
        if updated > now:
            return 'future updated_at'
        until = card.get('valid_until')
        if until is not None and timestamp(until) <= now:
            return 'expired'
    except (ValueError, TypeError, AttributeError):
        return 'invalid date'
    refs = card.get('source_refs')
    if not isinstance(refs, list) or not refs:
        return 'missing sources'
    for ref in refs:
        if not isinstance(ref, dict):
            return 'invalid source'
        if ref.get('type') not in ('user_supplied', 'official_website', 'official_document', 'crm', 'public_registry', 'third_party'):
            return 'invalid or inferred source'
        if ref.get('authority') not in ('S', 'A', 'B', 'C', 'D'):
            return 'invalid source authority'
        if not isinstance(ref.get('uri'), str) or not ref['uri'].strip():
            return 'source needs locator URI'
        try:
            if timestamp(ref['captured_at']) > now:
                return 'future source date'
        except (KeyError, ValueError, TypeError, AttributeError):
            return 'invalid source date'
    return None


def project_init(company, industry, intro_file, logo, output):
    company = company.strip()
    if not company:
        raise ValueError('company must not be empty')
    profile = next((p for p in profiles() if p['id'] == industry), None)
    if profile is None:
        raise ValueError('unknown industry; run industries')
    intro = Path(intro_file).read_text(encoding='utf-8').strip()
    if not intro:
        raise ValueError('introduction must not be empty')
    logo = Path(logo) if logo else None
    if logo and (not logo.is_file() or logo.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.svg')):
        raise ValueError('logo must be an existing PNG/JPEG/WebP/SVG file')
    logo_bytes = logo.read_bytes() if logo else b''
    if logo and not logo_bytes:
        raise ValueError('logo is empty')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name in ('private/raw', 'content'):
        (output / name).mkdir(parents=True)
    digest = hashlib.sha256(company.encode()).hexdigest().upper()
    tenant = 'company-' + uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    raw_logo = output / 'private/raw' / ('logo' + logo.suffix.lower()) if logo else None
    if raw_logo:
        raw_logo.write_bytes(logo_bytes)
    (output / 'private/raw/intro.txt').write_text(intro + '\n', encoding='utf-8')
    write(output / 'project.json', {'company': company, 'tenant_id': tenant, 'industry': industry,
          'domain': None, 'contact': None, 'identity_approved': False, 'contact_approved': False, 'markets': [], 'language': 'en',
          'language_is_design_assumption': True, 'stage': 'draft', 'created_at': now})
    write(output / 'industry.json', profile)
    schema = read(ROOT / 'assets/knowledge-card.schema.json')
    card = {k: '' for k in schema['required']}
    card.update(kb_id=f'RW-{digest[:6]}-0001', tenant_id=tenant, revision=1,
                module='02_company_identity', knowledge_kind='fact', entity_type='company',
                entity_id=tenant, title='待拆分核验的企业简介', language='zh-CN',
                status='pending_supplement', confidence=0,
                confidence_basis='用户提供资料，尚未拆分逐项核验', sensitivity='internal',
                public_claim_approved=False, role_views=['management', 'marketing'],
                conclusion=intro, conditions='待逐条确认后拆分为原子事实卡',
                source_refs=[{'type': 'user_supplied', 'uri': 'private/raw/intro.txt',
                              'captured_at': now, 'authority': 'C', 'locator': 'full introduction'}],
                pending_confirmations='身份、产品、联系方式、授权用途及量化主张待确认',
                created_at=now, updated_at=now, valid_until=None)
    write(output / 'private/knowledge-cards.json', [card])
    write(output / 'private/asset-register.json', [{'asset_id': 'logo-source', 'company_id': tenant,
          'file': str(raw_logo.relative_to(output)) if raw_logo else None, 'type': 'logo', 'source_uri': 'user_supplied',
          'captured_at': now, 'rights_status': 'unknown', 'rights_evidence': None,
          'visibility': 'internal', 'approval': 'draft', 'is_ai_generated': None,
          'intended_use': 'brand design input; confirm rights before public use',
          'claim_ids': [], 'derived_from': None, 'version': 1,
          'sha256': hashlib.sha256(logo_bytes).hexdigest(), 'language': None,
          'alt_text': company, 'width': None, 'height': None, 'used_on': []}] if logo else [])
    modules = read(ROOT / 'assets/module-catalog.json')['modules']
    write(output / 'private/module-coverage.json', [{'id': m['id'], 'title': m['title'],
          'status': 'pending_supplement', 'approved_cards': 0, 'expected_outputs': m['outputs']}
          for m in modules])
    write(output / 'content/page-manifest.json', [])
    write(output / 'content/public-facts.json', [])
    (output / 'private/gaps.md').write_text(
        '# 资料缺口\n\n先确认公司/品牌身份、主推产品、目标市场和询盘联系方式。\n\n'
        '## 行业参数\n\n' + '\n'.join('- ' + x for x in profile['product_fields']) +
        '\n\n## 所需证据\n\n' + '\n'.join('- ' + x for x in profile['evidence']) +
        '\n\n' + profile['missing_data_fallback'] + '\n', encoding='utf-8')
    (output / 'acceptance.md').write_text(
        '# 项目状态\n\n初始化已完成；网页、品牌设计、构建、部署、表单、收录与引用均 NOT_RUN。\n'
        '不得把整个项目目录作为静态服务器根目录。\n', encoding='utf-8')
    return output


def export(project):
    project = Path(project)
    meta = read(project / 'project.json')
    tenant = meta.get('tenant_id')
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError('project needs tenant_id')
    cards = read(project / 'private/knowledge-cards.json')
    if not isinstance(cards, list):
        raise ValueError('knowledge-cards must be an array')
    now = datetime.now(timezone.utc)
    ids = [c.get('kb_id') for c in cards if isinstance(c, dict)]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate knowledge IDs; resolve revisions before export')
    public, omitted = [], []
    for index, card in enumerate(cards):
        reason = eligibility(card, tenant, now)
        if reason:
            omitted.append({'index': index, 'reason': reason})
        else:
            public.append({key: card[key] for key in PUBLIC_KEYS})
    destination = project / 'content/public-facts.json'
    # ponytail: one local writer; add a per-project lock if concurrent exports are needed.
    temporary = destination.with_suffix('.tmp')
    write(temporary, public)
    temporary.replace(destination)
    write(project / 'private/public-export-report.json', {'exported': len(public),
          'omitted': omitted, 'checked_at': now.isoformat(),
          'scope': 'public projection guard only, not full schema or factual verification'})
    return {'exported': len(public), 'omitted': len(omitted)}


def self_test():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        (tmp / 'intro.txt').write_text('TEST ONLY: example machinery business.', encoding='utf-8')
        (tmp / 'logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
        project = project_init('TEST COMPANY', 'machinery', tmp/'intro.txt', tmp/'logo.svg', tmp/'site')
        assert export(project) == {'exported': 0, 'omitted': 1}
        cards = read(project / 'private/knowledge-cards.json')
        card = cards[0]
        card.update(status='verified_fact', sensitivity='public', public_claim_approved=True,
                    conclusion='Synthetic test fact only.', conditions='', title='Synthetic test')
        tenant = card['tenant_id']
        now = datetime.now(timezone.utc)
        assert eligibility(card, tenant, now) is None
        for changes in ({'tenant_id': 'other'}, {'status': 'conflicted'}, {'sensitivity': 'restricted'},
                        {'public_claim_approved': 'true'}, {'valid_until': '2000-01-01T00:00:00Z'},
                        {'valid_until': ''}, {'source_refs': []}, {'updated_at': 'not-a-date'},
                        {'conclusion': 12}, {'knowledge_kind': 'template'}):
            assert eligibility(dict(card, **changes), tenant, now), changes
        write(project / 'private/knowledge-cards.json', cards)
        assert export(project)['exported'] == 1
        projected = read(project / 'content/public-facts.json')[0]
        assert set(projected) == set(PUBLIC_KEYS)
        assert 'source_refs' not in projected and 'pending_confirmations' not in projected
        card['status'] = 'deprecated'
        write(project / 'private/knowledge-cards.json', cards)
        assert export(project)['exported'] == 0
        assert read(project / 'content/public-facts.json') == []
        try:
            project_init('TEST COMPANY', 'machinery', tmp/'intro.txt', tmp/'logo.svg', project)
        except FileExistsError:
            pass
        else:
            raise AssertionError('overwrite should be rejected')
        write(project / 'private/knowledge-cards.json', [card, card])
        try:
            export(project)
        except ValueError:
            pass
        else:
            raise AssertionError('duplicate IDs should be rejected')
    print('PASS: initialization, no overwrite, public allowlist, tenant/status/expiry/source gates, revocation, duplicate IDs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('industries')
    sub.add_parser('self-test')
    init = sub.add_parser('init')
    for arg in ('company', 'industry', 'intro-file', 'out'):
        init.add_argument('--' + arg, required=True)
    init.add_argument('--logo')
    publish = sub.add_parser('export')
    publish.add_argument('--project', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'industries':
            for item in profiles():
                print(item['id'] + '\t' + item['name'])
        elif args.command == 'init':
            print(project_init(args.company, args.industry, args.intro_file, args.logo, args.out))
        elif args.command == 'export':
            print(json.dumps(export(args.project), ensure_ascii=False))
        else:
            self_test()
    except (OSError, ValueError, TypeError, KeyError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
