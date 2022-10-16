import pathlib
import json
from typing import Dict
from fast_nilakkhana import process_file

repo_dir = pathlib.Path(__file__).absolute().parent.parent

root_files = [x for x in repo_dir.glob('root/**/*.json')]

translation_files = [x for x in repo_dir.glob('translation/**/*.json')]

comment_files = [x for x in repo_dir.glob('comment/**/*.json')]

print('Processing root text files[%d].'%(len(root_files)))
for file in root_files:
    process_file(file)
print('Root text files transformed.')

print('Processing translation text files[%d].'%(len(translation_files)))
for file in translation_files:
    process_file(file)
print('translation text files transformed.')

print('Processing comment text files[%d].'%(len(comment_files)))
for file in comment_files:
    process_file(file)
print('comment text files transformed.')