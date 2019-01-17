import lxml
import regex
import pathlib
from translate.storage.po import pofile

import config

def misc_fixes(filepath):
    if filepath.stem == 'info':
        return
    po = pofile(filepath.open('r'))
    changed = False
    for i, unit in enumerate(po.units):
        # Fix immersion
        for j, msgid in enumerate(unit.msgid):
            if 'immersion' in msgid:
                unit.msgid[j] = msgid.replace('immersion', 'samādhi')
                changed = True
        # fix evam
        evam_found = False
        if not evam_found and any(msgid.startswith('"Evaṃ me sutaṃ') for msgid in unit.msgid):
            evam_found = True
            if 'evam' not in ''.join(unit.automaticcomments):
                unit.automaticcomments += '#. <span class="evam">\n'
                po.units[i+1].automaticcomments.insert(0, '#. </span>\n')
                changed = True
        for j, comment in enumerate(unit.automaticcomments):
            new_comment, n = regex.subn(r'-pi([^a-z])', r'-pli\1', comment)
            if n:
                unit.automaticcomments[j] = new_comment
                changed = True
            new_comment, n = regex.subn(r'\bpi-', 'pli-', new_comment)
            if n:
                unit.automaticcomments[j] = new_comment
                changed = True            
            
    if changed:
        po.save()


if __name__ == '__main__':
    for file in config.PO_DIR.glob('**/*.po'):
        misc_fixes(file)
