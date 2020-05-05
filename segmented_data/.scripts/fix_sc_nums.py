import regex
from pathlib import Path

from common import print_name_if_needed


def increment_id(sc_id):
    return 'sc' + str(int(sc_id[2:]) + 1)

if __name__ == '__main__':
    files = sorted(Path('./html').glob('**/*.html'))

    for file in files:
        with file.open('r') as f:
            string = old_string = f.read()
        seen = set()
        
        last_id = None


        def repl_fn(m):
            global last_id
            sc_id = m[1]
            if sc_id in seen:
                print_name_if_needed('\n' + str(file))
                print(f'{sc_id} is duplicate')
                assert '-' not in sc_id
                sc_id = increment_id(last_id)
                result = m[0].replace(m[1], sc_id)
                changed = True
            else:
                result = m[0]

            seen.add(sc_id)
            last_id = sc_id
            return result
        string = regex.sub(r'data-ref=".*?(sc(\d+)(?:-\d+)?).*?"', repl_fn, string)
            
    
        if string != old_string:
            with file.open('w') as f:
                f.write(string)
    
    