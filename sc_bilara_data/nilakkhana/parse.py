import json
from pathlib import Path
from typing import Dict

from tqdm import tqdm

from parser import parse

WORK_DIR = Path(__file__).parent.parent

TARGET_FOLDERS = (
    WORK_DIR / 'root',
    WORK_DIR / 'translation',
    WORK_DIR / 'comment',
)


def update_file_content(file_content: Dict[str, str]) -> Dict[str, str]:
    for key, value in file_content.items():
        if type(value) != str:
            continue
        file_content[key] = parse(value).replace('"', '\'')
    return file_content


if __name__ == '__main__':
    for folder in TARGET_FOLDERS:
        print(f'{folder.name} folder in progress')
        for file in tqdm(folder.glob('**/*.json')):
            with open(file, 'r+', encoding='utf-8') as target_file:
                data = json.load(target_file)
                data = update_file_content(data)
                target_file.seek(0)
                target_file.truncate()
                json.dump(data, target_file, indent=2, ensure_ascii=False)
        print(f'{folder.name} done!')

    print('\nNilakkhana done!')
