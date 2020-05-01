import json
import pathlib
import regex

old_files = sorted(pathlib.Path('../').glob('[a-z]*/**/*.json'))

new_files = {
    file.name: file
    for file in
    pathlib.Path('./json-out').glob('**/*.json')
}


skip_rex = regex.compile(r'pli-tv-b[iu]-pm')

segment_id_mapping = {}

for file in old_files:
    
    if 'root' in file.stem and file.name in new_files and not skip_rex.search(file.stem):
        new_file = new_files[file.name]
    else:
        continue
    
    with file.open('r') as f:
        old_data = json.load(f)
    
    with new_files[file.name].open('r') as f:
        new_data = json.load(f)


    new_data_iter = iter(new_data.items())
    for segment_id, root_string in old_data.items():
        for new_segment_id, new_root_string in new_data_iter:
            print(f'{new_root_string} == {root_string}')
            if new_root_string == root_string:
                if new_segment_id != segment_id:
                    segment_id_mapping[segment_id] = new_segment_id
                break
        else:
            print('Something bad happened')
            raise ValueError
    
    for old_id, new_id in zip(old_data.keys(), new_data.keys()):
        segment_id_mapping[old_id] = new_id
    
    poooooooooooooooooooooo




for file in old_files:

    if file.name not in new_files:
        continue
    
    print(f'\n==={file.name}===\n')

    with file.open('r') as f:
        old_data = {
            segment_id_mapping.get(k, k): v 
            for k, v
            in json.load(f).items()}
    
    with new_files[file.name].open('r') as f:
        new_data = json.load(f)
    
    merged_data = {}
    for key, value in new_data.items():
        if key in old_data:
            merged_data[key] = old_data[key]
        else:
            merged_data[key] = new_data[key]

    with file.open('w') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
