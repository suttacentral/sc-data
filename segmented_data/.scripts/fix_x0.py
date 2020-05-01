import lxml.html
import pathlib
import regex


noact = True
HTML_DIR = pathlib.Path('./html')
for file in sorted(HTML_DIR.glob('**/*.html')):
    changed = False
    
    with file.open('r') as f:
        original_string = f.read()
    root = lxml.html.fromstring(original_string)
    elements = root.cssselect('a[data-uid]')
    for i, e in enumerate(elements):
        segment_id = e.get('data-uid')
        try:
            root_string = next(e.iter('i')).text_content().strip()
            translation_string = next(e.iter('b')).text_content().strip()
        except StopIteration:
            print(lxml.html.tostring(e, encoding='unicode'))
        if translation_string and not root_string:
            print(segment_id)
            next_id = elements[i+1].get('data-uid')
            if next_id[-1].isdigit():
                new_id = next_id + '^a'
                e.set('data-uid', new_id)
                changed = True
    
        if e[0].tag == 'i' and e[0].text_content() in {'', ' '}:
            
            new_id, n = regex.subn(r'.0([a-z])', r'^\1', segment_id)
            if n:
                e.set('data-uid', new_id)
                changed = True
            
    if changed:
        out_string =  lxml.html.tostring(root, encoding='unicode')
        out_string = '<!DOCTYPE html>\n' + out_string + '\n'
        with file.open('w') as f:
            f.write(out_string)

    