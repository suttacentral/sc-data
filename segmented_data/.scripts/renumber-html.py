import json
import regex
import pathlib
from itertools import zip_longest
from tempfile import NamedTemporaryFile
from collections import defaultdict

import lxml.html

from common import bilarasortkey

from num import DottedNum

def renumber_segments_anew(root, uid, numbering_basis, segment_id_mapping):
    elements = root.cssselect('a[data-uid]')

    last_num = DottedNum('0.0')

    changed = False

    dashed = regex.search(r'\d-\d', uid)

    for i, e in enumerate(elements):
        ref = e.get('data-ref')
        
            
        segment_id = old_segment_id = e.get('data-uid')
        if '^' in segment_id or segment_id[-1].isalpha():
            continue
        num = None
        if numbering_basis == 'pts-cs':
            cs_ref = None
            if ref:
                m = regex.search(r'pts-cs.*?((\d+(?:-\d+)?\.?)*)(,|$)', ref)
                if m:
                    cs_ref = m[1]
            if cs_ref:
                parts = cs_ref.split('.')
                if not dashed and len(parts) > 1:
                    num = DottedNum('.'.join(parts[1:]) + '.1')
                elif dashed and len(parts) > 0:
                    num = DottedNum(cs_ref + '.1')
                else:
                    num = DottedNum('1.1')
        elif numbering_basis == 'sc':
            if ref:
                m = regex.search(r'sc((\d+\.?)+)(,|$)', ref)
                if m:
                    sc_ref = m[1]
                    num = DottedNum(sc_ref + '.1')
        
        if num is None:
            num = DottedNum()
            num.make_one_greater(last_num)
        segment_id = segment_id.split(':')[0] + ':' + str(num)
        last_num = num

        if segment_id != old_segment_id:
            e.set('data-uid', segment_id)
            segment_id_mapping[old_segment_id].append(segment_id)
            changed = True
    
    return changed
        

        

def renumber_rootless(root):
    elements = root.cssselect('a[data-uid]')

    changed = False

    data = []
    for i, e in enumerate(elements):
        segment_id = old_segment_id = e.get('data-uid')
        root_e = get_root_e_create_if_needed(e)
        root_text = root_e.text_content().strip()
        if root_text:
            last_normal_id = segment_id
            last_normal_i = i
            continue
        
        is_heading = False
        for parent in e.iterancestors():
            if parent.tag in {'h1','h2','h3','h4','h5','h6', 'header'} or 'hgroup' in parent.get('class', ''):
                is_heading = True
                break
        
        char = chr(ord('a') + (i - last_normal_i - 1))
        if not is_heading:
            segment_id = last_normal_id + char
        else:
            next_normal_segment_id = None
            for j in range(i + 1, len(elements)):
                if get_root_e_create_if_needed(elements[j]).text_content().strip():
                    next_normal_segment_id = elements[j].get('data-uid')
                    break
            
            if next_normal_segment_id:
                segment_id = next_normal_segment_id + '^' + char

        if segment_id != old_segment_id:
            e.set('data-uid', segment_id)
            changed = True
    
    return changed
            

        

    

            
            
def get_root_e_create_if_needed(e):
    try:
        root_e = next(e.iter('i'))
    except StopIteration:
        root_e = lxml.html.fromstring('<i></i> ')
        e.insert(0, root_e)
    return root_e


            
problems = {}


def compare_strings(a, b, pattern, file):
    strings = []
    a_strings = a.split('\n')
    b_strings = b.split('\n')
    for i, (a_s, b_s) in enumerate(zip_longest(a_strings, b_strings)):
        a_m = regex.search(pattern, a)
        b_m = regex.search(pattern, b)
        
        strings.append((i, a_m[0] if a_m else None, b_m[0] if b_m else None))
    
    for lineno, a_s, b_s in strings:
        if a_s != b_s:
            print(f'{file.name}:{lineno}: Mismatch {a_s}, {b_s}')
            return False
    return True
        
segment_id_mapping = defaultdict(list)

noact = False
HTML_DIR = pathlib.Path('./html')
for file in sorted(HTML_DIR.glob('**/*.html')):
    print(str(file))
    with file.open('r') as f:
        original_string = f.read()

    if 'pts-cs' in original_string:
        numbering_basis = 'pts-cs'
    elif '"sc' in original_string:
        numbering_basis = 'sc'
    else:
        numbering_basis = None
        print('No numbering basis found for {file.name}')
        continue
        
    root = lxml.html.fromstring(original_string)

    changed = False
    
    
    changed = renumber_segments_anew(root, file.stem, numbering_basis, segment_id_mapping) or changed 
    changed = renumber_rootless(root) or changed

    segment_ids = [e.get('data-uid').split(':') for e in root.cssselect('a[data-uid]')]
    
    file_uid = regex.sub(r'(\D)(0+)', r'\1', file.stem)
    
    if not noact and changed:
        with file.open('w') as f:
            f.write(lxml.html.tostring(root, encoding='unicode'))

with open('segment_id_mapping.json', 'w') as f:
    json.dump(segment_id_mapping, f, indent=2)