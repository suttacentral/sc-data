import json
from pathlib import Path
from typing import Dict

from tqdm import tqdm

from fast_nilakkhana import process_file

WORK_DIR = Path(__file__).absolute().parent.parent

TARGET_FOLDERS = (
    WORK_DIR / 'root',
    WORK_DIR / 'translation',
    WORK_DIR / 'comment',
)





if __name__ == '__main__':
    for folder in TARGET_FOLDERS:
        print(f'{folder.name} folder in progress')
        for file in tqdm(folder.glob('**/*.json')):
           process_file(file)
        print(f'{folder.name} done!')

    print('\nNilakkhana done!')
