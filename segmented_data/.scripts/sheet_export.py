#!/usr/bin/env python3

import json
import argparse
import pyexcel
import regex
import sys



from common import iter_json_files, repo_dir, bilarasortkey, json_load, bcolors

def muid_sort_key(string):
    if string.startswith('root'):
        return (0, string)
    elif string.startswith('translation'):
        return (1, string)
    elif string.startswith('markup'):
        return (2, string)
    else:
        return (3, string)


def yield_rows(muid_strings, file_uid_mapping):
    fields = ['segment_id'] + muid_strings
    yield fields

    field_mapping = {field:i for i, field in enumerate(fields)}
    
    for file_num, (uid, file_mapping) in enumerate(file_uid_mapping.items()):
        data = {}
        segment_ids = set()
        for muid_string in muid_strings:
            if muid_string in file_mapping:
                file = file_mapping[muid_string]
                
                try:
                    file_data = json_load(file)
                except json.decoder.JSONDecodeError:
                    exit(1)
                
                i = field_mapping[muid_string]
                for segment_id, value in file_data.items():
                    if segment_id not in data:
                        data[segment_id] = [segment_id] + [''] * (len(fields) - 1)
                    data[segment_id][i] = value
        
        for segment_id in sorted(data.keys(), key=bilarasortkey):
            yield data[segment_id]
        
        if file_num < len(file_uid_mapping) - 1:
            yield [''] * len(fields)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export Spreadsheet")
    parser.add_argument('uid', nargs='+', help='One or more sutta UID to export')
    parser.add_argument('out', help='Output file')
    parser.add_argument('--include', default='', help='Filter by MUID. Comma seperated, + for and\nexample: "root,translation+en"')
    parser.add_argument('--exclude', default='', help='Filter by MUID. Comma seperated')
    args = parser.parse_args()

    uids = frozenset(args.uid)
    if args.include:
        include_filter = {frozenset(filter.split('+')) if '+' in filter else filter for filter in args.include.split(',')}
    else:
        include_filter = None
    if args.exclude:
        exclude_filter = frozenset(args.exclude.split(','))
    else:
        exclude_filter = None

    file_uid_mapping = {}
    for file in iter_json_files():
        
        
        uid, muids_string = file.stem.split('_')

        if not (uid in uids or any(part in uids for part in file.parent.parts)):
            continue
            
        print('Reading {}'.format(str(file.relative_to(repo_dir))))

        muids = frozenset(muids_string.split('-'))
        if include_filter:
            for muid in include_filter:
                if isinstance(muid, frozenset):
                    if muids.intersection(muid) == muid:
                        break
                else:
                    if muid in muids:
                        break
            else:
                continue
        
        if exclude_filter and exclude_filter.intersection(muids):
            continue
        
        if uid not in file_uid_mapping:
            file_uid_mapping[uid] = {}
        file_uid_mapping[uid][muids_string] = file
    
    if not file_uid_mapping:
        print('No matches for {}'.format(",".join(args.uid)), file=sys.stderr)
        exit(1)
        
    muid_strings = set()
    for keys in file_uid_mapping.values():
        muid_strings.update(keys)
    
    muid_strings = sorted(muid_strings, key=muid_sort_key)
    
    rows = yield_rows(muid_strings, file_uid_mapping)

    pyexcel.isave_as(array=rows, dest_file_name=args.out or (','.join(args.uid) + '.ods'))

        
        




