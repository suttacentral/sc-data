import lxml
import regex
import pathlib
import polib

source_dir = pathlib.Path('../').resolve()
print(source_dir)

po_dir = source_dir / 'po_text/dn/'

files = list(po_dir.glob('**/*.po'))

for filepath in files:
    if filepath.stem == 'info':
        continue
    po = polib.pofile(filepath)

    for i, entry in enumerate(po):
        if entry.msgid.startswith('Evaṃ me sutaṃ'):
            if 'evam' not in entry.comment:
                entry.comment = entry.comment + '<span class="evam">'
                po[i+1].comment = po[i+1].comment + '</span>'
                po.save()
                continue