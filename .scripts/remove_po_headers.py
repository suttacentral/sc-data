import regex
import config

def remove_header(string):
    assert string.startswith('msgid ""')
    string, num = regex.subn(r'^msgid "" *\nmsgstr "" *\n(".*" *\n)*', 'msgid ""\nmsgstr ""\n""\n', string)
    assert num == 1
    return string

if __name__ == '__main__':

    for file in config.PO_DIR.glob('**/*.po'):
        if file.stem == 'info':
            continue
        with file.open() as f:
            string = f.read()
        if string.startswith('#'):
            string = regex.sub(r'^#.*\n', '', string)
        
        string = remove_header(string)
        with file.open('w') as f:
            f.write(string)
