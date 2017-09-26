import os
import shutil
from bs4 import BeautifulSoup
from tqdm import tqdm

iso_mapping = {
    'pi': 'pli',
    'bo': 'xct',
    'sa': 'san',
    'pr': 'pra',
    'gr': 'pgd',
    'ug': 'uig',
}


def walk(directory):
    c = 0
    for path, dirs, files in tqdm(list(os.walk(directory))):
        # for folder in dirs:
        #     if folder in iso_mapping.keys():
        #         shutil.move(f'{path}/{folder}', f'{path}/{iso_mapping[folder]}')
        for file in files:
            if file.endswith('.html'):
                with open(f'{path}/{file}', 'r') as f:
                    html = f.read()
                soup = BeautifulSoup(html, 'lxml')
                div = soup.find('div', {'id': 'text'})
                if 'lang' in div:
                    if div['lang'] in iso_mapping.values():
                        # div['lang'] = iso_mapping[div['lang']]
                        c += 1
    print(c)


def main():
    walk('/home/jsemik/projects/suttaCentral/nextdata/html_text/')


if __name__ == '__main__':
    main()
