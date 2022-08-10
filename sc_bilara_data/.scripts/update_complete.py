import pathlib
import os
import sys
import shutil
import json
from subprocess import check_output, run, CalledProcessError
import time

from tempfile import TemporaryDirectory

os.chdir('..')

repo_dir = pathlib.Path('.')

root_files = list(repo_dir.glob('root/**/*.json'))

translation_files = set(repo_dir.glob('translation/**/*.json'))

git_branch_name = "complete_translations"

threshold = 99

complete_translations = set()

def chunks(l, n):
	for i in range(0, len(l), n):
		yield l[i:i+n]

def split_name(file):
	if not '_' in file.stem:
		return (None, None)
	return file.stem.split('_')


def calculate_completion(root_file, translation_file):
	root_data = json.loads(root_file.read_text())
	tr_data = json.loads(translation_file.read_text())
	return (len(root_data), len(tr_data))




uid_mapping = {}
long_id_mapping = {}

for file in root_files:
	uid, muids = split_name(file)
	if not uid:
		continue
	if uid not in uid_mapping:
		uid_mapping[uid] = []
	uid_mapping[uid].append(file)
	
	long_id_mapping[file.stem] = file


for file in sorted(translation_files):
	uid, muids = split_name(file)
	if uid not in uid_mapping:
		print(f'Could not find root file for {file.relative_to(repo_dir)}', file=sys.stderr)
		continue
	if len(uid_mapping[uid]) > 1:
		print(f'Multiple potential root files for {file.relative_to(repo_dir)}', file=sys.stderr)
	root_file = uid_mapping[uid][0]
	
	root_count, tr_count = calculate_completion(root_file, file)
	completion = int(0.5+100 * tr_count / root_count)
	
	assert root_count > 0
	
	if completion >= threshold or root_count - tr_count <= 1:
		complete_translations.add(file.name)

	

files = {'meta': [], 'root': []}

files['meta'] = [str(p) for p in repo_dir.glob('*.json')]

for folder in repo_dir.glob('[!.]*'):
	files[folder.name] = []
	for file in folder.glob('**/*.json'):
		if folder.name == 'translation' and file.name not in complete_translations:
			continue
		if file.stat().st_size <= 4:
			continue
		files[folder.name].append(str(file.relative_to(repo_dir)))
try:
	check_output(['git', 'checkout', 'master'])
	check_output(['git', 'stash', 'push', '--include-untracked', '-m', 'preserving master'])
	try:
		check_output(['git', 'checkout', git_branch_name])
	except CalledProcessError:
		print('Attempting to create branch')
		try:
			check_output(f'true | git mktree | xargs git commit-tree | xargs git branch {git_branch_name}', shell=True)
			check_output(['git', 'checkout', git_branch_name])
		except CalledProcessError:
			raise ValueError(f'Could not checkout branch {git_branch_name}')
		
		check_output(['git', 'commit', '--allow-empty', '--only', '-m', f'Created {git_branch_name}'])


	for folder, files_to_add in files.items():
		for chunk in chunks(files_to_add, 1000):
			check_output(' '.join(['git', 'checkout', 'master', '--', *chunk]), shell=True)
		time.sleep(0.1)
		try:
			check_output(['git', 'commit', '-a', '-m', f'Added updated files in {folder}'])
		except CalledProcessError:
				pass

finally:
	check_output(['git', 'checkout', 'master'])
	check_output(['git', 'stash', 'pop'])
	


	
	
