#!/usr/bin/env python310

""" Split HTML or XML files into sub-files.

The contents of every <split>....</split> tag range, will be put into
individual files, with no header or footer. The <split> tags themselves
will not appear in the output files.

"""

import re as regex
import pathlib
import argparse
import lxml.html
import lxml.etree
from logging import Logger

logger = Logger(__name__)

def parseargs():
    parser = argparse.ArgumentParser(description='Split a file on <split name="foo">')
    parser.add_argument('file', type=pathlib.Path)
    parser.add_argument('--out', type=pathlib.Path, default=None, help="Defaults to same location as source file")
    return parser.parse_args()


args = parseargs()
if not args.file.exists():
    logger.error('File `{}` does not exist'.format(args.file))
    exit(1)

if args.out is None:
    args.out = args.file.parent

if not args.out.exists():
    args.out.mkdir(parents=True)

XML = '.xml'
HTML = '.html'

modes = {XML, HTML}

mode = args.file.suffix

if mode not in modes:
    logger.error('Only works for .html and .xml files')
    exit(1)

if mode == HTML:
    doc = lxml.html.parse(str(args.file))
elif mode == XML:
    doc = lxml.etree.parse(str(args.file))
    
splits = doc.findall('//split')
if not splits:
    logger.error('No <split> tags found')
    exit(1)
    
for i, split in enumerate(splits):
    name = split.get('name', None)
    if not name:
        name = '{}-{}'.format(args.file.stem, i)
    outfile = (args.out / name).with_suffix(args.file.suffix)
    string = lxml.etree.tostring(split, encoding="unicode", method = {XML: 'XML', HTML: 'HTML'}[mode])
    string = regex.sub(r'(?s)<split[^>]*>(.*)</split>', r'\1', string)
    with outfile.open('w', encoding="utf8") as f:
        f.write(string)