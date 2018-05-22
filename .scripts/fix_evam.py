import lxml
import regex
import pathlib
from translate.storage.po import pofile

source_dir = pathlib.Path('../').resolve()
print(source_dir)

po_dir = source_dir / 'po_text/'

files = list(po_dir.glob('**/*.po'))

for filepath in files:
    if filepath.stem == 'info':
        continue
    po = pofile(filepath.open('r'))

    for i, entry in enumerate(po.units):
        if any(msgid.startswith('"Evaṃ me sutaṃ') for msgid in entry.msgid):
            print(entry.msgid)
            if 'evam' not in ''.join(entry.automaticcomments):
                entry.automaticcomments += '#. <span class="evam">\n'
                po.units[i+1].automaticcomments.insert(0, '#. </span>\n')
                po.save()
                continue