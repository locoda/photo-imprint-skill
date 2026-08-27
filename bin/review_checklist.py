#!/usr/bin/env python3
"""Record and validate page-level and set-level visual acceptance evidence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from workflow_contracts import QA_PAGE_CHECKS, QA_SET_CHECKS, digest, load_object, write_object


def status_of(checks: dict) -> str:
    values=[entry.get('status') for entry in checks.values() if isinstance(entry,dict)]
    return 'pass' if values and all(v=='pass' for v in values) else ('fail' if 'fail' in values else 'pending')

def recompute(data:dict)->None:
    pages=data.get('page_level_compliance',{}).get('pages',[])
    for page in pages:page['status']=status_of(page.get('checks',{}))
    data['page_level_compliance']['status']='pass' if pages and all(p.get('status')=='pass' for p in pages) else ('fail' if any(p.get('status')=='fail' for p in pages) else 'pending')
    data['set_level_cohesion']['status']=status_of(data.get('set_level_cohesion',{}).get('checks',{}))

def validate(data:dict)->list[str]:
    errors=[];pages=data.get('page_level_compliance',{}).get('pages')
    if not isinstance(pages,list) or not pages:return ['page-level checklist has no pages']
    for page in pages:
        number=page.get('page');checks=page.get('checks',{})
        for check in QA_PAGE_CHECKS:
            entry=checks.get(check)
            if not isinstance(entry,dict) or entry.get('status')!='pass':errors.append(f"page {number}: {check} is not pass")
            elif not str(entry.get('evidence','')).strip():errors.append(f"page {number}: {check} lacks evidence")
        for evidence_key in ('full_size_evidence','phone_scale_evidence'):
            path=Path(str(page.get(evidence_key,'')))
            if not path.is_file():errors.append(f"page {number}: missing {evidence_key} file")
    checks=data.get('set_level_cohesion',{}).get('checks',{})
    for check in QA_SET_CHECKS:
        entry=checks.get(check)
        if not isinstance(entry,dict) or entry.get('status')!='pass':errors.append(f"set: {check} is not pass")
        elif not str(entry.get('evidence','')).strip():errors.append(f"set: {check} lacks evidence")
    qpath=Path(str(data.get('qa_report_path','')))
    if not qpath.is_file() or digest(qpath)!=data.get('qa_report_sha256'):errors.append('locked QA report changed or is missing')
    recompute(data)
    if data.get('page_level_compliance',{}).get('status')!='pass':errors.append('page-level compliance is incomplete or failed')
    if data.get('set_level_cohesion',{}).get('status')!='pass':errors.append('set-level cohesion is incomplete or failed')
    return errors

def main()->int:
    p=argparse.ArgumentParser(description='Record or validate blocking manual visual-review evidence')
    sub=p.add_subparsers(dest='command',required=True)
    rec=sub.add_parser('record');rec.add_argument('--checklist',required=True,type=Path);rec.add_argument('--dimension',required=True,choices=('page','set'));rec.add_argument('--page',type=int);rec.add_argument('--check',required=True);rec.add_argument('--status',required=True,choices=('pass','fail'));rec.add_argument('--evidence',required=True);rec.add_argument('--note',default='')
    val=sub.add_parser('validate');val.add_argument('--checklist',required=True,type=Path)
    args=p.parse_args()
    try:data=load_object(args.checklist,'review checklist')
    except ValueError as exc:print(f"Checklist blocked: {exc}",file=sys.stderr);return 3
    if args.command=='record':
        allowed=QA_PAGE_CHECKS if args.dimension=='page' else QA_SET_CHECKS
        if args.check not in allowed:print(f"Checklist blocked: unknown {args.dimension} check {args.check}",file=sys.stderr);return 3
        if args.dimension=='page':
            if args.page is None:print('Checklist blocked: --page is required for page checks',file=sys.stderr);return 3
            pages=data.get('page_level_compliance',{}).get('pages',[]);target=next((x for x in pages if x.get('page')==args.page),None)
            if target is None:print(f"Checklist blocked: page {args.page} not found",file=sys.stderr);return 3
            target['checks'][args.check]={"status":args.status,"evidence":args.evidence,"note":args.note}
        else:data['set_level_cohesion']['checks'][args.check]={"status":args.status,"evidence":args.evidence,"note":args.note}
        recompute(data);write_object(args.checklist,data);print(f"Recorded {args.dimension} check {args.check}={args.status}");return 0
    errors=validate(data);write_object(args.checklist,data)
    if errors:print('Checklist validation failed:\n- '+'\n- '.join(errors),file=sys.stderr);return 4
    print('Checklist validation passed: page-level compliance and set-level cohesion both pass');return 0
if __name__=='__main__':raise SystemExit(main())
