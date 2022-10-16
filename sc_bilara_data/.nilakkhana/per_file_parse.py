import argparse
import json
from pathlib import Path
from typing import Dict

from fast_nilakkhana import process_file

# Set up argparse to get the files passed by git diff-tree
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-f', '--files', required=True, type=Path, nargs='*')
args = arg_parser.parse_args()

SUPPORTED_FILE_TYPES = ['comment', 'root', 'translation']

if __name__ == '__main__':
    """A modified version of .nilakkhana/parse.py that works on a list of files.
    The list of files represents files changed in a commit."""
    for file in args.files:
        # Skip running on html, variant, reference
        if file.parts[0] in SUPPORTED_FILE_TYPES:
            print(f'{file} file in progress')
            process_file(file)
            print(f'{file} done!')

    print('\nNilakkhana done!')
