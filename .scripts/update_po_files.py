import pathlib
import zipfile
import config

from remove_po_headers import remove_header
from misc_fixes import misc_fixes

po_dest = config.PO_DIR

po_source = pathlib.Path('./po_updates')


missing_dir = pathlib.Path('./missing')
if not missing_dir.exists():
    missing_dir.mkdir()
    for file in missing_dir.glob('.*'):
        file.unlink()

dest_map = {}


for folder in po_dest.glob('*'):
    if not folder.is_dir():
        continue
    dest_lang = folder.name.split('-')[-1]
    dest_map[dest_lang] = {}
    for file in folder.glob('**/*.po'):
        dest_map[dest_lang][file.stem] = file    
    

for file in po_source.glob('**/*'):
    if file.is_dir():
        continue
    if file.suffix == '.zip':
        print(f'Processing {file}')
    
    if 'tv' not in file.name:
        continue
    with file.open('rb') as f:
        zf = zipfile.ZipFile(f)
        
        for name in zf.namelist():
            path = pathlib.Path(name)
            parts = path.parts
            if '-' in parts[0]:
                lang = parts[0].split('-')[0]
            else:
                raise ValueError(name)
            uid = path.stem
            if uid == 'info':
                continue
            print(lang, uid)
            
            with zf.open(name, 'r') as f_z:
                string = f_z.read().decode('utf8')
            string = remove_header(string)
            try:
                dest_file = dest_map[lang][uid]
            except KeyError:
                print(f'Putting {uid} in missing_dir')
                dest_file = missing_dir / path.name
                
            with dest_file.open('w') as f:
                f.write(string)
            #misc_fixes(dest_file)
    break
