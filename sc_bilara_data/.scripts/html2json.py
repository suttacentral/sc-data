import lxml.html
import regex
import pathlib
import argparse
import pyexcel
import json

from html_lib import prune_html, rewrite_html, monolithic_markup_to_segment_markup

parser = argparse.ArgumentParser(description="Convert HTML to Bilara JSON files")
parser.add_argument('indir', help='Folder to process')
parser.add_argument('outdir', nargs='?', default='json-out', help='Directory to output JSON files to')
parser.add_argument('--translator', help='Default translator to use', default='sujato')
parser.add_argument('--translation-lang', help='Translation language', default='en')
parser.add_argument('--root-edition', help='Root edition', default='ms')
parser.add_argument('--root-lang', help='Root language', default='pli')



args = parser.parse_args()

outdir = pathlib.Path(args.outdir)
indir = pathlib.Path(args.indir)
root_lang = args.root_lang
translation_lang = args.translation_lang

root_edition = args.root_edition
translator = args.translator

all_files = sorted(indir.glob('**/*.html'))






def convert_to_data_and_markup(html_string):
    data = {
        "markup": {},
        "root": {},
        "translation": {},
        "ref": {},
        "var":  {},
        "note": {}
    }

    def subfn(m):
        fragment = lxml.html.fragment_fromstring(m[0])

        segment_id = fragment.get('data-uid')
        
        data['ref'][segment_id] = fragment.get('data-ref')
        data['var'][segment_id] = fragment.get('data-var')
        data['note'][segment_id] = fragment.get('data-note')

        for child in fragment:
            if child.tag == 'i':
                data['root'][segment_id] = child.text_content()
            elif child.tag == 'b':
                data['translation'][segment_id] = child.text_content()
            else:
                print('Can not recognize child element in {lxml.html.tostring(fragment, encoding="unicode")}')

        return '{' + segment_id + '}'

    markup_string = regex.sub(r"<a .*?data-uid='.*?'.*?>.*?</a>", subfn, html_string)

    for data_class, segment_data in data.items():
        for segment_id, segment in list(segment_data.items()):
            if not segment:
                segment_data.pop(segment_id)


    return data, markup_string

def save_data_to_json(data, file, outdir):
    base_root_path = f'{root_lang}/{root_edition}'
    base_relative_path = file.relative_to(indir).parent

    uid = file.stem

    root_file = outdir / 'root' / base_root_path / base_relative_path / f'{uid}_root-{root_lang}-{root_edition}.json'
    translation_file = outdir /  'translation' / translation_lang / translator / base_relative_path / f'{uid}_translation-{translation_lang}-{translator}.json'
    markup_file = outdir / 'markup' / base_relative_path / f'{uid}_markup.json'
    reference_file = outdir / 'reference' / base_relative_path / f'{uid}_reference.json'
    variant_file = outdir / 'variant' / base_root_path / base_relative_path / f'{uid}_variant-{root_lang}-{root_edition}.json'
    comment_file = outdir / 'comment' / translator / base_relative_path / f'{uid}_comment-{translation_lang}-{translator}.json'

    mapping = {
        "markup": markup_file,
        "root": root_file,
        "translation": translation_file,
        "ref": reference_file,
        "var":  variant_file,
        "note": comment_file
    }

    for key, target_file in mapping.items():
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open('w') as f:
            json.dump(data[key], f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    for file in all_files:
        with file.open('r') as f:
            html_string = f.read()
        
        html_string = prune_html(html_string)

        html_string = rewrite_html(html_string)

        

        data, monolithic_markup = convert_to_data_and_markup(html_string)

        data['markup'] = monolithic_markup_to_segment_markup(monolithic_markup)

        save_data_to_json(data, file, outdir)