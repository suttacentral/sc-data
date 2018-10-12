import regex
import pathlib
from itertools import zip_longest
from tempfile import NamedTemporaryFile

from config import PO_DIR, pofile, humansortkey

compare_dir = pathlib.Path('./compare')

noact = True

class Num:
    def __init__(self, string):
        if '-' in string:
            self.start, self.end = [int(num) for num in string.split('-')]
        else:
            self.start = self.end = int(string)
    
    def __repr__(self):
        if self.start == self.end:
            return str(self.start)
        return f'{self.start}-{self.end}'
    
    

def is_1_greater(a, b, uid, original_con):
    ones_count = 0
    
    if len(b) > len(a):
        a += [Num('0')]

    for i in range(0, min(len(a), len(b))):
        num_a = a[i]
        num_b = b[i]
        
        diff = num_b.start - num_a.end
        if diff == 1:
            ones_count += 1
    if ones_count != 1:
        if original_con.endswith('.0a'):
            return
        print(f"{uid}:{original_con}   {'.'.join(str(n) for n in a)} -> {'.'.join(str(n) for n in b)}")
        return False

def renumber_zeros(po):
    i = 1
    for unit in po.units:
        msgctxt = unit.msgctxt
        if not msgctxt:
            continue
        uid, num = msgctxt[0][1:-1].split(':')
        
        if num.startswith('0'):
            unit.msgctxt[0] = f'"{uid}:0.{i}"'
            i += 1
        else:
            return i > 1

def renumber_segments(po):
    changed = False
    last_nums = None
    for unit in po.units:
        msgctxt = unit.msgctxt
        if not msgctxt:
            continue
        uid, num = msgctxt[0][1:-1].split(':')
        
        nums = num.split('.')
        
        if last_nums and len(last_nums) in {2, 3} and len(last_nums) == len(nums):
            should_be_1 = False
            # try:
                # if int(nums[-2]) - int(last_nums[-2]) == 1:
                    # should_be_1 = True
            # except ValueError:
                # continue
            
            if nums[:-1] == last_nums[:-1]:
                m = regex.match(r'(\d+)([a-z]*)', last_nums[-1])
                last_num, last_alpha = m[1], m[2]
                m = regex.match(r'(\d+)([a-z]*)', nums[-1])
                num, alpha = m[1], m[2]

                if alpha:
                    continue
                if should_be_1:
                    new_num = '1'
                else:
                    new_num = str(int(last_num) + 1)
                if new_num != nums[-1]:
                    nums[-1] = new_num
                    new_ctxt = f'"{uid}:{".".join(nums)}"'
                    if msgctxt[0] != new_ctxt:
                        print(f'Replace: {msgctxt[0]} -> {new_ctxt}, {msgctxt[0] == new_ctxt}')
                        unit.msgctxt = [new_ctxt]
                        changed = True
        last_nums = nums
    return changed
            
            
            
            
problems = {}

def compare_order(a, b):
    nums_a = [l[1] for l in a]
    nums_b = [l[1] for l in b]
    if nums_a == nums_b:
        return False
    problems[a[0][0]] = (nums_a, nums_b)
    for i, j in zip(nums_a, nums_b):
        if i != j:
            print(f'{a[0][0]}: Sort Mismatch {i} != {j}')
            return



def check_ordering(contexts, file):
    
    compare_order(contexts, sorted(contexts, key=humansortkey))
    compare_order(contexts, sorted(reversed(contexts), key=humansortkey))
    

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
        
    

def is_data_intact(file, po):
    with file.open('r') as f:
        original = f.read()
    
    comparefile = compare_dir / file.relative_to(PO_DIR)
    comparefile.parent.mkdir(exist_ok=True, parents=True)
    with comparefile.open('wb') as f:
        po.savefile(f)  
    # pofile closes the file object so we need to reopen
    with open(f.name) as f2:
        new = f2.read()
    pattern = 'msgid ".*"'
    strings = []
    a_strings = original.split('\n')
    b_strings = new.split('\n')
    for i, (a_s, b_s) in enumerate(zip_longest(a_strings, b_strings, fillvalue='')):
        a_m = regex.search(pattern, a_s)
        b_m = regex.search(pattern, b_s)
        
        strings.append((i, a_m[0] if a_m else None, b_m[0] if b_m else None))
    
    for lineno, a_s, b_s in strings:
        if a_s != b_s:
            print(f'{file.stem}:{lineno}: Mismatch {a_s}, {b_s}')
            return False
    comparefile.unlink()
    return True



for file in sorted(PO_DIR.glob('**/*.po')):
    
    with file.open('r') as f:
        for lineno, string in enumerate(f, 1):
            if string.startswith('#. HTML'):
                if not regex.search(r'>\s*$', string):
                    print(f'{file.name}:{lineno} Malformed: {string}')
            for word, start in [('NOTE', '# NOTE:'),
                                ('VAR', '#. VAR:'),
                                ('REF', '#. REF:')]:
                if word in string and not string.startswith(start):
                    print(f'{file.name}:{lineno} Malformed: {string}')
                
    
    with file.open('r') as f:
        po = pofile(f)  
    
    if po.header() is None:
        print(f'{str(file)}: Header not readable!')
        with file.open('r') as f:
            lines = []
            for line in f:
                if line.startswith('msgid'):
                    break
                lines.append(line)
        cruft = '\n'.join(lines)
        print(f'File starts with: {cruft}')
    
    intact = is_data_intact(file, po)
    if not intact:
        print(f'Not saving {file.name} because not intact')
        continue
    
    changed = False
    if 'np' in file.name:
        changed = renumber_zeros(po)
    
    changed = renumber_segments(po) or changed 
    
    contexts = []
    for unit in po.units:    
        msgctxt = unit.msgctxt
        if msgctxt:
            contexts.append(msgctxt[0][1:-1].split(':'))
    
    
    check_ordering(contexts, file)
    
    file_uid = regex.sub(r'(\D)(0+)', r'\1', file.stem)
    nums = []
    last_nums = None
    for uid, con in contexts:
        if file_uid != uid:
            print(f'Mismatched UID: {uid} in {file_uid}')
        
        con2 = regex.sub(r'[a-z]$', lambda m: '.'+str(ord(m[0])-96), con )
        nums = [Num(num) for num in con2.split('.')]
        if last_nums is not None:
            is_1_greater(last_nums, nums, uid, con)
            
        
        last_nums = nums
    
    
    if not noact and changed and intact:
        with file.open('wb') as f:
            po.savefile(f)
