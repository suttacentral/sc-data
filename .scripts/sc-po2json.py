#!/usr/bin/env python

import os

import time
import regex
import hashlib
import logging
import pathlib
import argparse
import datetime
import lxml.html

from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po

import logging
import json

import polib
import regex
import lxml


def parse_args():
    parser = argparse.ArgumentParser(description='Convert HTML to PO',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--flat', action='store_true', help="Don't use relative paths")
    parser.add_argument('-z', '--no-zfill', action='store_true', help="Don't zfill numbers")
    parser.add_argument('--out', type=str, help="Destination Folder")
    parser.add_argument('--lang', type=str, default='pi', help='Language Code')
    parser.add_argument('--strip-tags',
                        type=str,
                        help="CSS selector for stripping tags but leaving text",
                        default=".ms, .msdiv, .t, .t-linehead, .tlinehead, .t-byline, .t-juanname, .juannum, .mirror-right, .cross")
    parser.add_argument('--strip-trees',
                        type=str,
                        help="CSS selector for removing entire element trees",
                        default="#metaarea, .mirror-left, p.suttainfo")
    parser.add_argument('-v', '--verbose', action='store_true');
    parser.add_argument('infiles', type=str, nargs='+', help="Source HTML Files")
    return parser.parse_args()
    
args = parse_args()


class PoProcessingError(Exception):
    pass
    
def remove_leading_zeros(string):
    return regex.sub(r'([A-Za-z.])0+', r'\1', string)

def strip_number_from_title(title):
    title = title.replace('​','')
    return regex.sub(r'[\d\.\{\} –-]*', '', title, 1)

def sanitize_title(title):
    #If stripping the number returns an empty string, return that so suttaplex picks up
    # the root title instead.
    return strip_number_from_title(title)

def tilde_to_html_lists(po):
    for entry in po:
        if '~' in entry.msgstr:
            if not entry.msgstr.startswith('~'):
                raise ValueError('Case not handled: msgstr contains but does not start with ~')
                
            entry.msgstr = ('<ol><li>' + 
                            '</li><li>'.join(entry.msgstr.split('~')[1:]) + 
                            '</li></ol>'
                            )

def ref_match_repl(m):
    return ''.join(
        '<a class="{}" id="{}"></a>'.format(_class, _id) 
            for _class, _id in zip(m.captures(1), m.captures(2)))

def clean_html(string):
    out = regex.sub(r'<html>.*<body>', r'', string, flags=regex.DOTALL).replace('\n', ' ')
    out = out.replace('HTML: ', '')
    out = regex.sub(r'REF: (?:([a-z]+)([\w.-]+),?\s*)+', ref_match_repl, out)
    out = regex.sub(r'>\s*VAR.*?<', '><', out)
    out = out.replace('</p>', '</p>\n')
    out = out.replace('</blockquote>', '</blockquote>\n')
    root = lxml.html.fromstring(out)
    out = lxml.html.tostring(root, encoding='unicode')
    return out

def extract_strings_from_po(po):
    markup = []
    msgids = {}
    msgstrs = {}

    for entry in po:
        markup.append(entry.comment + f'<sc-seg id="{entry.msgctxt}"></sc-seg>')
        if entry.msgid:
            msgids[entry.msgctxt] = entry.msgid
        if entry.msgstr:
            msgstrs[entry.msgctxt] = entry.msgstr

    markup = clean_html(''.join(markup))

    return {
        'markup': markup,
        'msgids': msgids,
        'msgstrs': msgstrs,
    }


def extract_headings_from_po(po):
    # If the title only contains numbers, an empty string is returned so the
    # suttaplex only picks up the original title instead.
    found = {'tr': {}, 'root': {}}
    for string, key in ( ('<h1', 'title'), ('class="division"', 'division') ):
        tr_strings = []
        root_strings = []
        for entry in po[:10]:
            if string in entry.comment:
                found['tr'][key] = sanitize_title(entry.msgstr)
                found['root'][key] = sanitize_title(entry.msgid)
    return found


po_files = []
for infile in args.infiles:
    infile = pathlib.Path(infile)
    if infile.is_dir():
        po_files.extend(infile.glob('**/*.po'))
    else:
        po_files.append(infile)


def indent_json(string):
    data = json.loads(string)
    return json.dumps(data, ensure_ascii=False, indent=2)


out_dir = pathlib.Path('json-out') if not args.out else pathlib.Path(args.out)
if not out_dir.exists():
    out_dir.mkdir()

markup_dir = out_dir / 'markup'
strings_dir = out_dir / 'source'

for po_file in sorted(po_files):
    po = polib.pofile(po_file)
    
    tilde_to_html_lists(po)
    
    data = extract_strings_from_po(po)
    
    uid = remove_leading_zeros(po_file.stem)
    
    msgids_file = strings_dir / '/'.join(po_file.parent.parts[1:]) / f'{uid}.json'
    markup_file = markup_dir / '/'.join(po_file.parent.parts[1:]) / f'{uid}.json'
    
    markup_file.parent.mkdir(exist_ok=True, parents=True)
    msgids_file.parent.mkdir(exist_ok=True, parents=True)
    
    with markup_file.open('w') as f:
        f.write(data['markup'])
    with msgids_file.open('w') as f:
        json.dump(data['msgids'], f, ensure_ascii=False, indent=2)
