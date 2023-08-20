"""This module is used to get files that are related to changed or deleted files.  Since the bilara-data-integrity tests
are now only run on a per file basis, we need to make sure that when an html file is modified the tests are run on both
the html and root file.  This module will also make sure that if an hmtl file is deleted, it’s related root file is also
deleted.

This is the list of the relationships between tests and files in bilara-data-integrity:
Test                     ->  Files
------------------------------------------------
bilara_check_comment     ->  comment and root
bilara_check_html        ->  html and root
bilara_check_reference   ->  only reference
bilara_check_root        ->  only root
bilara_check_translation ->  translation and html
bilara_check_variant     ->  variant and root
"""

import argparse
import os
import sys
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import List

# Set up argparse to get changed or deleted files passed to the module
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-f', '--files', required=True, type=Path, nargs='*')
args = arg_parser.parse_args()

DIRECTORIES = ['comment', 'html', 'reference', 'root', 'translation', 'variant']


def _build_paths_data_dict(file_paths: List[Path]) -> dict:
    """Creates a dictionary where the key is the file ID, like an1.1-10,
    and the value is a list of root directories, like [html, translation].
    Operates on the file paths given to the script."""
    paths_dict = defaultdict(list)
    for file_path in file_paths:
        # Like html, root, variant
        root_dir = file_path.parts[0]
        # Like an1.1-10
        file_id_parts = file_path.stem.split('_')
        # If the split resulted in only 1 element, then the file_id didn't have an underscore.
        # This means the file_id didn't follow the usual convention, and might cause problems if processed.
        # So we want to skip it.
        if len(file_id_parts) <= 1:
            continue

        paths_dict[file_id_parts[0]].append(root_dir)

    return paths_dict


def get_related_files(file_paths: List[Path]) -> None:
    """Finds the file paths related to those given to the script. So if
        html/pli/ms/sutta/mn/mn17_html.json
    is given to the script, it will return:
        reference/pli/ms/sutta/mn/mn17_reference.json,
        root/pli/ms/sutta/mn/mn17_root-pli-ms.json,
        translation/en/sujato/sutta/mn/mn17_translation-en-sujato.json,
        html/pli/ms/sutta/mn/mn17_html.json
    The script will not create duplicates.  So the
        html/pli/ms/sutta/mn/mn17_html.json
    that appears at the end of the list is the path given to the script."""
    file_paths_data = _build_paths_data_dict(file_paths=file_paths)
    all_files = []

    for file_id, root_dirs in file_paths_data.items():
        if not file_id:
            # These might be top level files, like _author, _category, etc.
            continue
        related_dirs = deepcopy(DIRECTORIES)
        # To avoid getting duplicates of the files given to the script,
        # exclude their directories.
        for root_dir in root_dirs:
            related_dirs.remove(root_dir)

        for related_dir in related_dirs:
            for walk_root, _, walk_files in os.walk(related_dir):
                for walk_file in walk_files:
                    walk_file_id = walk_file.split('_')[0]
                    if walk_file_id == file_id:
                        all_files.append(os.path.join(walk_root, walk_file))

    all_files.extend([str(p) for p in file_paths])
    print(' '.join(all_files))


if __name__ == '__main__':
    try:
        get_related_files(file_paths=args.files)
    except Exception as e:
        sys.exit(1)
