#!/usr/bin/env python3

from pathlib import Path

bilara_data_dir = Path('../../bilara-data')
scb_data_dir = Path('../sc_bilara_data')

def prune(files):
    return {f for f in files if not f.parts[0].startswith('.')}

bilara_files = prune(file.relative_to(bilara_data_dir) for file in bilara_data_dir.glob('**/*.json'))

scb_files = prune(file.relative_to(scb_data_dir) for file in scb_data_dir.glob('**/*.json'))

to_delete = scb_files - bilara_files
print(f'Deleting {len(to_delete)} files')
for file in to_delete:
    (scb_data_dir / file).unlink()