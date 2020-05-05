import regex
from pathlib import Path

from common import print_name_if_needed


if __name__ == '__main__':
    files = sorted(Path('./html').glob('**/*.html'))

    for file in files:
        with file.open('r') as f:
            string = old_string = f.read()
        seen = set()
        
        last_id = None


        def repl_fn(m):
            global last_id
            pts_cs_id = m[1]
            if pts_cs_id in seen:
                print_name_if_needed('\n\n' + str(file))
                print(f'{pts_cs_id} is duplicate')

            seen.add(pts_cs_id)
            last_id = pts_cs_id
            return m[0]
        string = regex.sub(r'data-ref=".*?pts-cs.*?((\d+\.?)+(?:-\d+)?).*?"', repl_fn, string)
    
    