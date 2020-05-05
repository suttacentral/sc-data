#!/usr/bin/env python3

import json
import argparse
import pyexcel
import regex
import sys
from itertools import groupby
from common import iter_json_files, json_load, repo_dir, bilarasortkey

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Renumber Segment IDS based on spreadsheet")
    parser.add_argument('file', help='Spreadsheet file to import. CSV, TSV, ODS, XLS')
    parser.add_argument('--original', help='Old spreadsheet, used for updates')
    parser.add_argument('-q', '--quiet', help='Do not display changes to files')
    args = parser.parse_args()

    original_rows = pyexcel.iget_records(file_name=args.original)
    new_rows = pyexcel.iget_records(file_name=args.file)

    segment_id_mapping = {}

    for old, new in zip(original_rows, new_rows):
        segment_id_mapping[old['segment_id']] = new['segment_id']
      
    
    for file in iter_json_files():
        data = json_load(file)
        
        new_data = {}
        changed = False

        for k, v in data.items():
            if k in segment_id_mapping:
                k = segment_id_mapping[k]
                changed = True
            new_data[k] = v
        if changed:
            print(f'Updated {file}')
            with file.open('w') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            

