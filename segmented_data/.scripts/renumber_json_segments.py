import json
import regex
import pathlib

segment_id_mapping = json.load(open('segment_id_mapping.json'))


json_files = sorted(pathlib.Path('../').glob('[a-z]*/**/*.json'))

json_root_files = sorted(pathlib.Path('../').glob('[a-z]*/**/*root*.json'))

html_files = sorted(pathlib.Path('./html').glob('**/*.html'))


master_segment_id_mapping = {}

segment_id_mapping = {}
for html_file in html_files:
    with html_file.open('r') as f:
        string = f.read()
    uid = regex.sub(r'(a-z)0+', r'\1', html_file.stem)
    segment_ids = regex.findall(f'data-uid="([^:]+\:[a-z0-9.^-]+)"', string)
    segment_id_mapping[uid] = segment_ids


for file in json_root_files:

    with file.open('r') as f:
        data = json.load(f)
    
    uid, _ = file.stem.split('_')
    
    if uid not in segment_id_mapping:
        continue
    segment_ids = segment_id_mapping[uid]

    if len(segment_ids) != len(data):
        print(f'Length mismatch for {file}')
        continue

    new_data = {}
    for i, (segment_id, value) in enumerate(data.items()):
        new_id = segment_ids[i]
        if segment_id != new_id:
            new_data[segment_ids[i]] = value
            master_segment_id_mapping[segment_id] = new_id

    with file.open('w') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
