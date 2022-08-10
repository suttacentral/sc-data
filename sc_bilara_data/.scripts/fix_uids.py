from pathlib import Path
import regex
from num import DottedNum



files = sorted(Path('./html').glob('**/*.html'))

from common import print_name_if_needed


for file in files:
    file_uid = regex.sub(r'0+(\d+)', r'\1', file.stem.split('_')[0])

    with file.open('r') as f:
        string = f.read()

    def repl(m):
        uid = m[1]

        if uid != file_uid:
            print(f'Uid mismatch in {file}: {uid}')
            return m[0].replace(uid, file_uid)
        
        return m[0]
    
    
    string, n = regex.subn(r'data-uid="([^:]+)\:([a-z0-9.^-]+)"', repl, string)
    
    if n > 0:
        with file.open('w') as f:
            f.write(string)
