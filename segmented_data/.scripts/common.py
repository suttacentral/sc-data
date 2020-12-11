import sys
import json
import regex
import pathlib

repo_dir = pathlib.Path(__file__).parent.parent

def iter_json_files(glob_pattern='**/[!_]*.json'):
    yield from sorted(repo_dir.glob(f'[!_.]*/{glob_pattern}'), key=lambda f: humansortkey(str(f)))

def numericsortkey(string, _split=regex.compile(r'(\d+)').split):
    # if regex.fullmatch('\d+', s) then int(s) is valid, and vice-verca.
    return [int(s) if i % 2 else s for i, s in enumerate(_split(str(string)))]


def humansortkey(string, _split=regex.compile(r'(\d+(?:[.-]\d+)*)').split):
    """
    >>> humansortkey('1.1') > humansortkey('1.0')
    True

    >>> humansortkey('1.0a') > humansortkey('1.0')
    True

    >>> humansortkey('1.0^a') > humansortkey('1.0')
    True
    """
    # With split, every second element will be the one in the capturing group.
    return [numericsortkey(s) if i % 2 else s
            for i, s in enumerate(_split(str(string)))]

def bilarasortkey(string):
    """
    >>> bilarasortkey('1.1') > bilarasortkey('1.0')
    True

    >>> bilarasortkey('1.0a') > bilarasortkey('1.0')
    True

    >>> bilarasortkey('1.0^a') < bilarasortkey('1.0')
    True
    """

    if string[-1].isalpha():
        string = f'{string[:-1]}.{ord(string[-1])}'
    subresult = humansortkey(string)

    result = []
    for i, obj in enumerate(subresult):
        if obj == '':
            obj = 0
        if isinstance(obj, str) and obj and obj[0] == '^':
                result.extend([-1, obj[1:]])
        else:
            result.append(obj)
    
    if isinstance(result[-1], list):
        result.append(0)
    return result


def print_name_if_needed(file, _seen=set()):
    if file not in _seen:
        print(file)
    _seen.add(file)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def json_load(file):
    try:
        with file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.decoder.JSONDecodeError as e:
        lineno = e.lineno
        colno = e.colno
        with file.open('r') as f:
            lines = f.readlines()
        
        print('{}JSONDecodeError{}: {}'.format(bcolors.FAIL, bcolors.ENDC, file), file=sys.stderr)
        for i in range(lineno-2, lineno):
            if i >= 0:
                print(bcolors.OKGREEN+bcolors.BOLD, str(i).rjust(6), bcolors.ENDC, '  ', lines[i], sep='', end='', file=sys.stderr)
        print(' '*(colno + 7), '^', sep='', file=sys.stderr)
        print(bcolors.FAIL, e.msg, bcolors.ENDC, sep='', file=sys.stderr)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
