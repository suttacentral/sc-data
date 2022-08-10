import json
import regex
from pathlib import Path
from difflib import SequenceMatcher

from common import bilarasortkey



old_json_files = [p for p in Path('../').glob('**/*.json') if '.scripts' not in p.parts]
new_json_files = {file.name:file for file in Path('./json-out/').glob('**/*.json')}

all_segment_id_mappings = {}

class HorrificTuple(tuple):

    def __hash__(self):
        return hash(self[1])
    def __eq__(self, other):
        return self[1] == other[1]


def get_uid(file):
    return file.stem.split('_')[0]

for old_file in old_json_files:
    if 'root' not in old_file.name:
        continue
    if old_file.name not in new_json_files:
        continue
    new_file = new_json_files[old_file.name]
    
    with old_file.open() as f:
        old_data = [HorrificTuple(t) for t in json.load(f).items()]

    with new_file.open() as f:
        new_data = [HorrificTuple(t) for t in json.load(f).items()]
    

    sm = SequenceMatcher()
    sm.set_seqs(old_data, new_data)

    all_segment_id_mappings[get_uid(old_file)] = segment_id_mapping = {}

    for match in sm.get_matching_blocks():
        i,j,n = match

        old_matches = old_data[i:i+n]
        new_matches = new_data[j:j+n]

        for old, new in zip(old_matches, new_matches):
            assert old[1] == new[1]

            segment_id_mapping[old[0]] = new
        
        for segment_id, string in old_matches:
            if segment_id not in segment_id_mapping:
                print(f'"{segment_id}": "{string}" missed')

# The segment id mapping has now been generated

for old_file in old_json_files:
    if old_file.name not in new_json_files:
        continue
    
    new_file = new_json_files[old_file.name]

    segment_id_mapping = all_segment_id_mappings[get_uid(old_file)]

    with old_file.open() as f:
        old_data = json.load(f)
    
    with new_file.open() as f:
        new_data = json.load(f)

    merged_data = {}
    for segment_id, value in old_data.items():
        original_segment_id = segment_id
        if segment_id in segment_id_mapping:
            segment_id = segment_id_mapping[segment_id][0]
            if 'root' in old_file.name:
                assert value == segment_id_mapping[original_segment_id][1]
        merged_data[segment_id] = value

    final_data = {}
    for segment_id in new_data:
        if segment_id in merged_data:
            value = merged_data[segment_id]
        else:
            value = new_data[segment_id]
        final_data[segment_id] = value
    if 'root' in old_file.name:
        assert list(final_data) == sorted(final_data, key=bilarasortkey)

    with old_file.open('w') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)


    