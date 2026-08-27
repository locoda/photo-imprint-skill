#!/usr/bin/env python3
"""Lock staged outputs, package only verified files, and verify release ZIP integrity."""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from PIL import Image
from workflow_contracts import digest, load_object, write_object
from review_checklist import validate as validate_checklist

IMAGE_RE=re.compile(r'^(\d+)\.(png|webp|jpg|jpeg)$',re.I)

def stage(args)->int:
    candidates=[p for p in args.input.iterdir() if IMAGE_RE.match(p.name)]
    if any(p.is_symlink() for p in candidates):raise ValueError('staging directory contains a symlinked image')
    files=sorted(p for p in candidates if p.is_file())
    if not files:raise ValueError('staging directory has no numbered image files')
    entries=[]
    for p in files:
        with Image.open(p) as im:w,h=im.size
        entries.append({'page':int(IMAGE_RE.match(p.name).group(1)),'filename':p.name,'sha256':digest(p),'bytes':p.stat().st_size,'width':w,'height':h})
    pages=[x['page'] for x in entries]
    if pages!=list(range(1,len(pages)+1)):raise ValueError(f'numbered pages must be contiguous from 1: {pages}')
    write_object(args.output,{'schema_version':'1.0.0','staging_directory':str(args.input.resolve()),'files':entries})
    print(f'Locked {len(entries)} staged images in {args.output}');return 0

def verify_stage(directory:Path,manifest:dict)->list[Path]:
    paths=[];expected={x['filename'] for x in manifest.get('files',[])}
    actual={p.name for p in directory.iterdir() if p.is_file() and IMAGE_RE.match(p.name)}
    if actual!=expected:raise ValueError(f'staged files differ from manifest: expected {sorted(expected)}, got {sorted(actual)}')
    for entry in manifest['files']:
        p=directory/entry['filename']
        if p.is_symlink():raise ValueError(f'staged file became a symlink: {p.name}')
        if digest(p)!=entry['sha256']:raise ValueError(f'staged file changed: {p.name}')
        with Image.open(p) as im:
            if list(im.size)!=[entry['width'],entry['height']]:raise ValueError(f'dimensions changed: {p.name}')
        paths.append(p)
    return paths

def package(args)->int:
    stage_manifest=load_object(args.staging_manifest,'staging manifest');paths=verify_stage(args.input,stage_manifest)
    checklist=load_object(args.review_checklist,'review checklist')
    checklist_errors = validate_checklist(checklist)
    if checklist_errors:
        raise ValueError('review checklist is incomplete: ' + '; '.join(checklist_errors))
    if checklist.get('page_level_compliance',{}).get('status')!='pass':raise ValueError('page-level compliance is not complete/pass')
    if checklist.get('set_level_cohesion',{}).get('status')!='pass':raise ValueError('set-level cohesion is not complete/pass')
    qpath=Path(str(checklist.get('qa_report_path','')))
    if not qpath.is_file() or digest(qpath)!=checklist.get('qa_report_sha256'):raise ValueError('QA report is missing or changed')
    state=load_object(args.state,'approval state')
    if state.get('status') not in {'batch_approved','revision_in_progress','revision_completed'}:raise ValueError('approval/revision state does not permit packaging')
    for stem in ('render_plan','production_plan','sample','sample_plate'):
        path_value, expected = state.get(f'{stem}_path'), state.get(f'{stem}_sha256')
        if path_value is not None or expected is not None:
            path = Path(str(path_value))
            if not path.is_file() or digest(path) != expected:
                raise ValueError(f'locked {stem} changed or is missing')
    if state.get('render_plan_path'):
        locked_plan = load_object(Path(state['render_plan_path']), 'locked render plan')
        config_lock = locked_plan.get('resolved_config_lock')
        if isinstance(config_lock, dict):
            path = Path(str(config_lock.get('path', '')))
            if not path.is_file() or digest(path) != config_lock.get('sha256'):
                raise ValueError('locked resolved config changed or is missing')
        for reference in locked_plan.get('style_reference_locks', []):
            for stem in ('image', 'source_metadata'):
                path = Path(str(reference.get(f'{stem}_path', '')))
                if not path.is_file() or digest(path) != reference.get(f'{stem}_sha256'):
                    raise ValueError(f"locked style reference {reference.get('id')} {stem} changed or is missing")
    revision=state.get('active_revision')
    if isinstance(revision,dict):
        baseline=revision.get('baseline_stage',{});stale=set(revision.get('stale_pages',[]))
        current={e['page']:e['sha256'] for e in stage_manifest['files']}
        for page,old_hash in baseline.items():
            page=int(page)
            if page not in stale and current.get(page)!=old_hash:raise ValueError(f'unchanged approved page {page} was modified')
            if page in stale and current.get(page)==old_hash:raise ValueError(f'stale revision page {page} was not replaced')
    release={'schema_version':'1.0.0','files':[{k:e[k] for k in ('page','filename','sha256','bytes','width','height')} for e in stage_manifest['files']],
        'verification':{'page_level_compliance':'pass','set_level_cohesion':'pass','qa_report_sha256':checklist['qa_report_sha256']}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    manifest_bytes=(json.dumps(release,indent=2,ensure_ascii=False)+'\n').encode()
    with zipfile.ZipFile(args.output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(p,p.name)
        z.writestr('release-manifest.json',manifest_bytes)
    write_object(args.manifest_output,release)
    with zipfile.ZipFile(args.output) as z:
        bad=z.testzip()
        if bad:raise ValueError(f'ZIP integrity failed at {bad}')
    if state.get('status') == 'revision_in_progress':
        state['status'] = 'revision_completed'
        state['last_verified_package'] = {'path': str(args.output.resolve()), 'sha256': digest(args.output)}
        state.pop('active_revision', None)
        write_object(args.state, state)
    print(f'Packaged verified staged files to {args.output}');return 0

def verify(args)->int:
    with zipfile.ZipFile(args.zip) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('ZIP contains duplicate members')
        for info in z.infolist():
            name = info.filename
            p=Path(name)
            if p.is_absolute() or '..' in p.parts:raise ValueError(f'unsafe ZIP member: {name}')
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError(f'symlink ZIP member is forbidden: {name}')
        if 'release-manifest.json' not in names:raise ValueError('release-manifest.json missing')
        manifest=json.loads(z.read('release-manifest.json'))
        expected_order=[e['filename'] for e in manifest.get('files',[])]+['release-manifest.json']
        if names!=expected_order:raise ValueError(f'ZIP members/order mismatch: {names}')
        import hashlib
        for e in manifest['files']:
            raw=z.read(e['filename'])
            if hashlib.sha256(raw).hexdigest()!=e['sha256']:raise ValueError(f"checksum mismatch: {e['filename']}")
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    if list(image.size) != [e['width'], e['height']]:
                        raise ValueError(f"dimension mismatch: {e['filename']}")
                    image.verify()
            except ValueError:
                raise
            except Exception as exc:
                raise ValueError(f"undecodable image: {e['filename']}: {exc}") from exc
        bad=z.testzip()
        if bad:raise ValueError(f'ZIP integrity failed at {bad}')
    print('ZIP verification passed');return 0

def main()->int:
    p=argparse.ArgumentParser(description='Stage and package only hash-locked, QA-approved carousel outputs')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('stage');s.add_argument('--input',required=True,type=Path);s.add_argument('--output',required=True,type=Path);s.set_defaults(handler=stage)
    b=sub.add_parser('package');b.add_argument('--input',required=True,type=Path);b.add_argument('--staging-manifest',required=True,type=Path);b.add_argument('--review-checklist',required=True,type=Path);b.add_argument('--state',required=True,type=Path);b.add_argument('--output',required=True,type=Path);b.add_argument('--manifest-output',required=True,type=Path);b.set_defaults(handler=package)
    v=sub.add_parser('verify');v.add_argument('--zip',required=True,type=Path);v.set_defaults(handler=verify)
    args=p.parse_args()
    try:return args.handler(args)
    except (ValueError,OSError,json.JSONDecodeError,zipfile.BadZipFile) as exc:print(f'Packaging blocked: {exc}',file=sys.stderr);return 4
if __name__=='__main__':raise SystemExit(main())
