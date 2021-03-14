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
                        default=".ms, .msdiv, .t, .t-linehead, .tlinehead, .scribe, .t-juanname, .juannum, .mirror-right, .cross")
    parser.add_argument('--strip-trees',
                        type=str,
                        help="CSS selector for removing entire element trees",
                        default="#metaarea, .mirror-left, p.suttainfo")
    parser.add_argument('-v', '--verbose', action='store_true');
    parser.add_argument('infiles', type=str, nargs='+', help="Source HTML Files")
    return parser.parse_args()
    
args = parse_args()

logger = logging.Logger('sc-html2po')
handler = logging.StreamHandler()
logger.addHandler(handler)
if args.verbose:
    handler.setLevel('INFO')
else:
    handler.setLevel('WARN')

strip = args.strip_tags
remove = args.strip_trees
infiles = []
for infile in args.infiles:
    infile = pathlib.Path(infile)
    if infile.is_dir():
        infiles.extend(infile.glob('**/*.html'))
    else:
        infiles.append(infile)

if args.out:
    outpath = pathlib.Path(args.out)
else:
    outpath = pathlib.Path('./po-out')
if not outpath.exists():
    outpath.mkdir(parents=True)

def cleanup(element):
    for e in element.cssselect(strip):
        if not regex.search('\w', e.text_content()):
            e.drop_tree()
        else:
            e.drop_tag()
    for e in element.cssselect(remove):
        e.drop_tree()

void_tags ={'area',
            'base',
            'br',
            'col',
            'command',
            'embed',
            'hr',
            'img',
            'input',
            'keygen',
            'link',
            'meta',
            'param',
            'source',
            'track',
            'wbr'}

from enum import Enum

class TokenType(Enum):
    comment = 1
    text = 2
    newline = 3
    comment_note = 4
    end = 9
    

class Token:
    def __init__(self, type, value, ctxt=None, msgstr=''):
        self.type = type
        self.value = value
        self.ctxt = ctxt
        self.msgstr = msgstr
    
    def __repr__(self):
        return 'Token(TokenType.{}, "{}")'.format(self.type.name, self.value)

class Html2Po:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.mangle_dict = {}
        self.mangle_lookup = {}
        self.token_stream = []
    
    def make_open_tag(self, e):
        attribs = ' '.join('{}="{}"'.format(k, v)
                            for k, v 
                            in sorted(e.attrib.items()))
        
        return '<{}{}{}>'.format(e.tag,
                                 ' ' if attribs else '',
                                 attribs)

    def make_close_tag(self, e):
        return '</{}>'.format(e.tag)
    
    def mangle_repl(self, m):
        if m[0] in self.mangle_lookup:
            mangle_key = self.mangle_lookup[m[0]]
        else:
            mangle_key = 'MANG{}{}GLE'.format('R' if m[0][1] == '/' else 'O', len(self.mangle_dict))
            self.mangle_lookup[m[0]] = mangle_key
            self.mangle_dict[mangle_key] = m[0]
        return mangle_key

    def demangle_repl(self, m):
        return self.mangle_dict[m[0]]

    def mangle(self, html_string):
        return regex.sub('<[^<]+>', self.mangle_repl, html_string)

    def demangle(self, html_string):
        return regex.sub(r'MANG.[0-9]+GLE', self.demangle_repl, html_string)

    def segment_inner(self, e):
        
        msgstr_mapping = {}
        def sanitize_key(key):
            return regex.sub(r'[\p{punct}\s]', '', key).casefold()
            
        msgstr_elements = e.cssselect('[data-msgstr]')
        for msgstr_element in msgstr_elements:
            msgstr_mapping[sanitize_key(msgstr_element.text_content())] = {'value': msgstr_element.get('data-msgstr'), 'used': False}
        for msgstr_element in msgstr_elements:
            msgstr_element.drop_tag()
        
        variant_notes = {}
        var_elements = e.cssselect('.var')
        for var_element in var_elements:
            variant_notes[var_element.text_content()] = 'VAR: {} → {}'.format(var_element.text_content(), var_element.get('title'))
        for var_element in var_elements:
            var_element.drop_tag()
        
        html_string = lxml.html.tostring(e, encoding='unicode').strip()
        html_string = html_string.replace('\n', ' ').replace('\xa0', ' ').replace('\xad', '')
        m = regex.match(r'<[^<]+>[ \n\t]*(.*)</\w+>', html_string, flags=regex.DOTALL)
        if not m:
            raise ValueError(html_string)
            
        html_string = m[1]
        m = regex.match(r'(?i)((?:<a[^<]*></a>[ \n\t]*)*)(.*)', html_string)
        if m[1]:
            self.add_token(TokenType.comment, m[1])
            html_string = m[2]
        html_string = self.mangle(html_string)
        logger.info(html_string)
        pattern = r'(?<!\d+)([.;:!?—，。：；！…？—](?:\p{punct}+|[ \n\t]*MANG.[0-9]+GLE[\p{punct}\d]*MANG.[0-9]+GLE)*[\u200b\s]*|(?<!^)…[ \n\t]*(?:pe[ \n\t]*…[ \n\t]*)?[.;:!?—；：。，，。：；！…？—]*)(?:MANGR[0-9]+GLE)*'
        parts = regex.split(pattern, html_string)
        segments = [''.join(parts[i:i+2]).strip() for i in range(0, len(parts), 2)]
        
        for i, segment in list(enumerate(segments)):
            m = regex.match(r'(?r)[「「『]$', segment)
            if m:
                print(segments[i], segments[i+1], segment[-1] + segments[i + 1])
                segments[i + 1] = segment[-1] + segments[i + 1]
                segments[i] = segment[:-1]
        sentence_count = 0
        for segment in segments:
            if not segment:
                continue
            segment = self.demangle(segment)
            lines = regex.split('(<br[^>]*>|(?:<a [^>]+></a>)*$)', segment)
            for i in range(0, len(lines), 2):
                line = lines[i].strip()
                if line:
                    m = regex.match(r'^[ \n\t]*(</\w+>)(.*)', line, flags=regex.DOTALL)
                    if m:
                        if self.token_stream[-1].type == TokenType.newline and self.token_stream[-2].type == TokenType.text:
                            self.token_stream[-2].value += m[1]
                            line = m[2].strip()
                    sentence_count += 1
                    ctxt = '{}:{}.{}'.format(self.uid, self.paragraph_count, sentence_count)
                    msgstr = ''
                    
                    for var_text in list(variant_notes):
                        if var_text in line:
                            self.add_token(TokenType.comment_note, variant_notes.pop(var_text))
                    if line and not line.isspace():
                        try:
                            key = sanitize_key(lxml.html.fromstring(line).text_content())
                        except Exception as e:
                            globals().update(locals())
                            raise
                            
                        if key in msgstr_mapping:
                            msgstr_mapping[key]['used'] = True
                            msgstr = msgstr_mapping[key]['value']
                        self.add_token(TokenType.text, line, ctxt, msgstr)
                
                if i + 1 < len(lines):
                    br = lines[i + 1].strip()
                    if br:
                        self.add_token(TokenType.comment, br)
                self.add_token(TokenType.newline)
        
        for key, obj in msgstr_mapping.items():
            if obj['used'] == False:
                print('Failed to find use for {}: {}'.format(key, obj['value']))
    
    def add_token(self, type, value=None, ctxt=None, msgstr=''):
        self.token_stream.append(Token(type, value, ctxt, msgstr))
    
    def recursive_deconstruct(self, element):
        
        self.add_token(TokenType.comment, self.make_open_tag(element))
        if element.tag in {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.paragraph_count += 1
            self.segment_inner(element)
        else:
            for child in element:
                self.recursive_deconstruct(child)
        
        if element.tag not in void_tags:
            self.add_token(TokenType.comment, self.make_close_tag(element))
            if element.tag == 'html':
                self.add_token(TokenType.end)
        
    def preamble(self):
        return r'''
msgid ""
msgstr ""
'''
    
    def pretty_string(self, string):
        string = regex.sub(r'(?i)\n(\n#: <br[^>]*>)', r'\1', string)
        string = regex.sub(r'\n(\n(?:#: </\w+>(?:\n|$))+)', r'\1\n', string)
        return string
    
    def create_catalog(self):
        catalog = Catalog(
            locale=None,
            domain=None,
            fuzzy=False,
            header_comment='',
            project='suttas',
            version='1',
            msgid_bugs_address='sujato@gmail.com',
            creation_date=datetime.datetime.utcnow(),
            language_team="SuttaCentral",
            charset="UTF-8"
        )
        
        comments = []
        comment_notes = []
        prev_token = None
        for token in self.token_stream:
            if token.type == TokenType.comment:
                if comments: # and prev_token and prev_token.type == TokenType.comment:
                    comments[0] += token.value.strip()
                else:
                    comments.append(token.value.strip())
            elif token.type == TokenType.comment_note:
                comment_notes.append(token.value)
            elif token.type == TokenType.text:
                comments.extend(comment_notes)
                comment_notes.clear()
                catalog.add(id=token.value.strip().replace('\n', ' ').replace('"', '"'),
                            string=token.msgstr or '',
                            auto_comments=comments,
                            context=token.ctxt
                )
                comments.clear()
            elif token.type == TokenType.newline:
                pass
            elif token.type == TokenType.end:
                break
            else:
                raise ValueError('{} is not a valid type'.format(token.type))
            prev_token = token
        return catalog
    
    def process(self, filename):        
        doc = lxml.html.parse(filename)
        root = doc.getroot()
        cleanup(root)
        self.root = root
        self.paragraph_count = 0
        self.uid = pathlib.Path(filename).stem
        self.recursive_deconstruct(root)

common_path = None
if not args.flat and len(infiles) > 0:
    common_path = pathlib.Path(*os.path.commonprefix([(p if p.is_dir() else p.parent).parts for p in infiles]))

class ZFiller:
    def __init__(self):
        self.tree = {}
        self.seen = set()
    
    def split(self, string):
        return [int(part) if part.isdigit() else part 
                for part
                in regex.findall(r'\p{alpha}+|\d+|[^\p{alpha}\d]+', string)]
    
    def add_files(self, files):
        for file in files:
            string = file.relative_to(common_path)
            parts = self.split(str(string))
            branch = self.tree
            for part in parts:
                if part not in branch:
                    branch[part] = {}
                branch = branch[part]
                self.seen.add(part)
    
    def zfill(self, string):
     try:
        parts = self.split(string)
        out = []
        branch = self.tree
        for part in parts:
            if isinstance(part, int):
                maxlen = len(str(max(branch.keys())))
                out.append(str(part).zfill(maxlen))
            else:
                out.append(part)
            branch = branch[part]
        return ''.join(out)
     except Exception as e:
         globals().update(locals())
         raise

if not args.no_zfill:
    z = ZFiller()
    z.add_files(infiles)

for file in infiles:
    print(file.stem)
    if common_path:
        outfile = file.relative_to(common_path)
    else:
        outfile = file.stem        
        
    if not args.no_zfill:
        outfile = z.zfill(str(outfile.parent / outfile.stem))
    outfile = outpath / (str(outfile) + '.po')
    try:
        outfile.parent.mkdir(parents=True)
    except FileExistsError:
        pass
    
    html2po = Html2Po()
    try:
        html2po.process(str(file))
    except Exception as e:
        logging.exception(file)
        raise
    catalog = html2po.create_catalog()
    with outfile.open('wb') as f:
        write_po(f, catalog, width=-1)
    
    with outfile.open() as f:
        string = oldstring = f.read()

    string = regex.sub(r'\s*(msgid ""\nmsgstr ""\n)(".*"\n)+', r'\1', string)
    
    # join comments into one
    string = regex.sub(r'#. VAR: (?<note>.+)\n(?:#\. (?<note>(?!VAR).+)\n)*', lambda m: '#. VAR: ' + ' '.join(m.captures('note')) + '\n', string)



    def wrangle_html(m):

        string = ' '.join(m.captures(1))

        refs = []
        
        def wrangle_anchor(m2):

            root = lxml.html.fromstring(m2[0])
            if len(root.attrib) == 2 and 'id' in root.attrib and 'class' in root.attrib and not root.text:
                a_id = root.get('id')
                a_class = root.get('class')
                if a_id.startswith(a_class):
                    refs.append(a_id)
                    return ""
                if a_class == "sc":
                    refs.append("sc" + a_id)
                    return ""

            
            print(f"Don't know how to handle: {m2[0]}")
            return m2[0]
        
        string = regex.sub(r'<a .*?></a>', wrangle_anchor, string)

        out = []
        if string and not string.isspace():
            string = regex.sub(r'<html.*?>(<section)', r'\1', string)
            out.append('#. HTML: ' + string + '\n')
        if refs:
            out.append('#. REF: ' + ', '.join(refs) + '\n')
        return ''.join(out)


    string = regex.sub(r'(?:#\. ((?!VAR).+)\n)+', wrangle_html, string)

    with outfile.open('w') as f:
        f.write(string)


