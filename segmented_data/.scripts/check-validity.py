import json
from pathlib import Path
import regex

import difflib

from common import bilarasortkey

merged_json_files = list(Path('../root/').glob('**/*.json'))

source_json_files = list(Path('./json-out/root').glob('**/*.json'))

mapping = {
    file.name: file for file in source_json_files
}

for file in merged_json_files:
    if file.name not in mapping:
        continue
    
    source_data = json.load(mapping[file.name].open())
    merged_data = json.load(file.open())

    for key, value in source_data.items():
        if merged_data.get(key) != value:
            print(f'Value for {key} not "{value}" instead "{merged_data.get(key)}"')
    
    
    ids = list(merged_data.keys())
    sorted_ids = sorted(merged_data.keys(), key=bilarasortkey)
    if ids != sorted_ids:
        print(f'\n\nSort mismatch in {file}')
        print('\n'.join(difflib.context_diff(ids, sorted_ids)))
        
    

