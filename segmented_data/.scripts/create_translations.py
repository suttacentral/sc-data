#!/usr/bin/env python

import pathlib
import os
import sys
import json
import subprocess
os.chdir('..')
repo_dir = pathlib.Path('./')

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True, type=str, help='Source folder, e.g.: root/pli/ms')
parser.add_argument('--target', required=True, type=str, help='Target folder, e.g.: translation/en/sujato')
parser.add_argument('-n', '--dry-run', action='store_true', help="Perform no actions")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--uid', default=None, type=str, help='UID of division/subdivision to translate, e.g.: dn')
group.add_argument('--uids', default=None, type=str, help='UIDs of suttas to translate, e.g.: dn1,dn2,dn3')


args = parser.parse_args()

uid = args.uid
uids = args.uids.split(',') if args.uids else None

if not uid and not uids:
    print('Either uid or uids must be specified', file=sys.stderr)

source = args.source
target = args.target


source_dir = repo_dir / source
target_dir = repo_dir / target

assert source_dir.exists()

source_files = []

if uid:
    matches = list(source_dir.glob(f'**/{uid}'))
    if matches:
        assert len(matches) == 1
        source_files.extend(matches[0].glob('**/*.json'))
if uids:
    for file in source_dir.glob('**/*.json'):
        if file.name.split('_')[0] in uids:
            source_files.append(file)

if not source_files:
    print('No Source Files Found')

print('Creating translation files')
target_muids = target.replace('/', '-')
new_files = []
for file in source_files:
    new_parent = target_dir / file.parent.relative_to(source_dir)
    new_name = file.stem.split('_')[0] + '_' + target_muids + '.json'
    new_file = new_parent / new_name 
    new_files.append(new_file)
    if not new_file.exists():
        if args.dry_run:
            print(f'Create {str(new_file)}')
        else:
            new_parent.mkdir(parents=True, exist_ok=True)
            with new_file.open('w') as f:
                json.dump({}, f, indent=2)
    
if args.dry_run:
    print(f'git add {len(new_files)} files')
else:
    subprocess.run(['git', 'add', *new_files])





    
    
