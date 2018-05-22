from config import source_dir, pofile

files = source_dir.glob('**/*.po')

for file in files:
    changed = False
    po = pofile(file.open())
    for unit in po.units:
        for i, msgid in enumerate(unit.msgid):
            if 'immersion' in msgid:
                unit.msgid[i] = msgid.replace('immersion', 'samādhi')
                changed = True
    if changed:
        po.save()