#!/usr/bin/env python3

import logging
import json
import argparse
import pyexcel
import regex
import sys
from itertools import groupby
from common import iter_json_files, repo_dir, bilarasortkey

def check_segment_id(segment_id, file):
    if segment_id.count(':') != 1:
        logging.error(f'Segment ID "{segment_id}" in "{str(file)} is malformed, expected a single ":", but {segment_id.count(":")} found')
        return False
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import Spreadsheet")
    parser.add_argument('file', help='Spreadsheet file to import. CSV, TSV, ODS, XLS')
    parser.add_argument('-q', '--quiet', help='Do not display changes to files')
    args = parser.parse_args()

    rows = pyexcel.iget_records(file_name=args.file)
    
    files = {file.stem: file for file in iter_json_files()}

    segment_uid_to_file_mapping = {}

    def get_file(uid, muids):
        filestem = f'{uid}_{muids}'
        if filestem in files:
            return files[filestem]

        uid_stem = regex.match(r'[a-z]+(\d+\.)?', uid)[0]

        rex = regex.compile(f'{regex.escape(uid_stem)}.*_{muids}')

        if muids not in segment_uid_to_file_mapping:
            segment_uid_to_file_mapping[muids] = {}

        for i in range(0, 2):
            file = segment_uid_to_file_mapping[muids].get(uid)
            if file:
                return file
            if i > 0:
                break

            for filestem, file in files.items():
                if rex.fullmatch(filestem):
                    with file.open('r') as f:
                        data = json.load(f)
                    for segment_id in data:
                        if check_segment_id(segment_id, file):
                            segment_uid = segment_id.split(':')[0]
                            segment_uid_to_file_mapping[muids][segment_uid] = file
        
        raise ValueError('Could not find file for {}_{}'.format(uid, muids))

    errors = 0
    for uid, group in groupby(rows, lambda row: row['segment_id'].split(':')[0]):
        group = list(group)
        fields = list(group[0].keys())[1:]
        data = {field: {} for field in fields}
        
        for record in group:
            segment_id = record['segment_id']
            if not segment_id:
                continue
            if not check_segment_id(segment_id, args.file):
                errors += 1
                continue
            for field in fields:
                value = record[field]
                if value:
                    data[field][segment_id] = value
        
        for field in fields:
            if not data[field]:
                continue
            file = get_file(uid, field)
            if not file:
                print('ERROR: Could not find file for {}_{}'.format(uid, field), file=sys.stderr)
                errors += 1
                continue

            with file.open('r') as f:
                old_data = json.load(f)
            
            merged_data = {}

            segment_ids = sorted(set(old_data) | set(data[field]), key=bilarasortkey)

            for segment_id in segment_ids:
                old_value = old_data.get(segment_id)
                if not old_value:
                    # Maybe do something here
                    pass
                value = data[field].get(segment_id)
                if value is None:
                    # Doesn't exist in spreadsheet
                    value = old_value
                value = str(value) if isinstance(value, int) else value
                old_value = str(old_value) if isinstance(value, int) else old_value
                if not args.quiet and old_value != value:
                    print('{uid}_{field}:{segment_id}: {old_value} -> {value}'.format(**locals()))
                merged_data[segment_id] = value

            with file.open('w') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
    if errors > 0:
        print(f'{errors} occured while importing sheet, not all data was imported', file=sys.stderr)
        exit(1)
    exit(0)