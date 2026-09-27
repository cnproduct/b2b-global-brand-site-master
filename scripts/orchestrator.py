#!/usr/bin/env python3
"""One entry point: private evidence -> brand -> static pages -> local validation."""
import argparse
import json
import sys
import tempfile
from pathlib import Path
import sitekit
from site_compiler import build, origin, starter, EMAIL
from validate_site import audit_site

ALIASES = {'stone_cladding':'building-materials','consumer_electronics':'electronics',
           'auto_parts':'automotive','eco_packaging':'packaging','solar_energy':'energy',
           'home_appliances':'appliances','pet_products':'pet-products'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', help='Rebuild an existing V2 project into a fresh site directory')
    parser.add_argument('--name')
    intro = parser.add_mutually_exclusive_group()
    intro.add_argument('--intro')
    intro.add_argument('--intro-file')
    parser.add_argument('--industry')
    parser.add_argument('--domain')
    parser.add_argument('--email')
    parser.add_argument('--logo')
    parser.add_argument('--out', help='New private project directory; refuses to overwrite')
    parser.add_argument('--site-out', help='Optional new static output directory; refuses to overwrite')
    parser.add_argument('--brand-color')
    parser.add_argument('--release', action='store_true', help='Require editorial/fact approvals; does not deploy')
    args = parser.parse_args()
    try:
        if args.project:
            if any((args.name,args.intro,args.intro_file,args.industry,args.domain,args.email,args.logo,args.out,args.brand_color)):
                raise ValueError('edit the existing project files, then use --project without initialization options')
            project = Path(args.project)
        else:
            if not args.name or not args.industry or not args.out or not (args.intro or args.intro_file):
                raise ValueError('new project requires --name --industry --out and --intro/--intro-file')
            if args.release:
                raise ValueError('initialize a draft first; review evidence and content before release')
            domain = origin(args.domain)
            if args.email and not EMAIL.fullmatch(args.email):
                raise ValueError('invalid email')
            industry = ALIASES.get(args.industry,args.industry)
            if industry in ('hygiene_medical','chemicals_pharma'):
                raise ValueError('ambiguous legacy industry; choose hygiene/medical or chemicals/food explicitly')
            with tempfile.TemporaryDirectory() as temporary:
                intro_path = Path(args.intro_file) if args.intro_file else Path(temporary)/'intro.txt'
                if not args.intro_file:
                    intro_path.write_text(args.intro, encoding='utf-8')
                project = sitekit.project_init(args.name,industry,intro_path,args.logo,args.out)
            meta = sitekit.read(project/'project.json')
            meta.update(domain=domain,contact=args.email)
            sitekit.write(project/'project.json',meta)
            config = starter(project)
            config['primary_color'] = args.brand_color
            sitekit.write(project/'content/site.json',config)
        destination = build(project,args.release,args.site_out)
        meta = sitekit.read(project/'project.json')
        report = audit_site(destination,args.release,origin(meta.get('domain')))
        sitekit.write(project/'private/local-validation.json',report)
        state=sitekit.read(project/'private/latest-build.json');state['status']=report['status']
        sitekit.write(project/'private/latest-build.json',state)
        (project/'acceptance.md').write_text('# Build acceptance\n\n'
            f'Local static checks: {report["status"]}\n\nSite directory: {destination}\n\n'
            'Mode: '+('reviewed release candidate' if args.release else 'noindex draft')+'\n\n'
            'Browser review, HTTP deployment, inquiry receipt, indexing, AI visibility and conversion: NOT_RUN.\n'
            'Only deploy the reported site directory, never the whole project.\n',encoding='utf-8')
        print(json.dumps({'site_directory':str(destination),'local_checks':report['status'],
                          'mode':'release_candidate' if args.release else 'draft','deployed':False},ensure_ascii=False,indent=2))
        return 0 if report['status']=='PASS' else 1
    except (OSError,ValueError,TypeError,KeyError) as error:
        print('ERROR: '+str(error),file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
