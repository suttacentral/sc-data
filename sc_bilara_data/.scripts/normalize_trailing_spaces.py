import pathlib
import json

repo_dir = pathlib.Path(__file__).absolute().parent.parent

filtered_root_files = [x for x in repo_dir.glob('root/**/*.json') if x.name.find(
    'site') == -1 and x.name.find('blurb') == -1 and x.name.find('name') == -1]

filtered_translation_files = [x for x in repo_dir.glob('translation/**/*.json') if x.name.find(
    'site') == -1 and x.name.find('blurb') == -1 and x.name.find('name') == -1]

variant_files = [x for x in repo_dir.glob('variant/**/*.json')]

comment_files = [x for x in repo_dir.glob('comment/**/*.json')]

def process_file(file):
    with open(file, 'r+', encoding='utf8') as f:
        text = json.load(f)
        f.seek(0)
        f.truncate()
        new_text = {}
        for k,v in text.items():
            if len(v.rstrip()) != 0:
                new_value = v.rstrip()
            else:
                new_value = v
            if len(new_value) > 0 and new_value[-1] != '—' and len(new_value.strip()) != 0:
                new_text[k] = new_value.ljust(len(new_value) + 1, ' ')
            else:
                new_text[k] = new_value
        json.dump(new_text, f, indent=2, ensure_ascii=False)


print('Processing root text files[%d].'%(len(filtered_root_files)))
for file in filtered_root_files:
    process_file(file)
print('Root text files processed.')


print('Processing translation text files[%d].'%(len(filtered_translation_files)))
for file in filtered_translation_files:
    process_file(file)
print('translation text files processed.')


print('Processing variant text files[%d].'%(len(variant_files)))
for file in variant_files:
    process_file(file)
print('variant text files processed.')


print('Processing comment text files[%d].'%(len(comment_files)))
for file in comment_files:
    process_file(file)
print('comment text files processed.')
