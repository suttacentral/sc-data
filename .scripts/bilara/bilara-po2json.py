import json
import regex
import pathlib
import subprocess
from translate.storage.po import pofile

import sys

sys.path.insert(0, "..")

from config import PO_DIR, numericsortkey

NOTE_PREFIX = "NOTE: "
HTML_PREFIX = "HTML: "
REF_PREFIX = "REF: "

OUT_DIR = pathlib.Path("./out")


def unzfill(string):
    return regex.sub(r'(\D)0+(\d+)', r'\1\2', string)

def text_dump(string, file):
    if not file.parent.exists():
        file.parent.mkdir(parents=True)
    with file.open('w') as f:
        f.write(string)


def json_dump(data, file, even_if_empty=False):
    if not data:
        if not even_if_empty:
            return
    if not file.parent.exists():
        file.parent.mkdir(parents=True)
    with file.open('w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_project_name(uid):
    if uid.startswith("pli-"):
        return "vinaya"
    else:
        return "sutta"


def get_translator_name(project):
    if project == "vinaya":
        return "brahmali"
    else:
        return "sujato"


def hacked_numericsortkey(obj):
    string = str(obj)
    string = string.replace("info.po", "!info.po")
    return numericsortkey(string)


po_files = sorted(PO_DIR.glob("**/kn/**/*"), key=hacked_numericsortkey)


def parse_info_po(po):
    return {unit.getsource(): unit.gettarget() for unit in po.units[1:]}


def printif(obj):
    if obj:
        print(obj)


last_info = None
last_info_file = None

done_file = pathlib.Path('.done.json')

if done_file.exists():
    with done_file.open('r') as f:
        done = json.load(f)
else:
    done = {}

for file in po_files:
    if str(file) in done:
        continue
    if file.is_dir():
        if not last_info_file:
            continue
        if str(file).startswith(str(last_info_file.parent)):
            continue
        else:
            print(f"Clearing info because {file} is not parent")
            last_info = None
            last_info_file = None
            continue
    rel_file = file.relative_to(PO_DIR)

    langs = rel_file.parts[0]
    if "-" in langs:
        root_lang, translation_lang = langs.split("-")

    project_dir = rel_file.parts[1:-1]

    with file.open("rb") as f:
        po = pofile(f)
    if file.name == "info.po":
        last_info = parse_info_po(po)
        last_info_file = file
        continue

    rel_parts = file.relative_to(PO_DIR).parts
    division = rel_parts[1]
    root_lang, translation_lang = rel_parts[0].split("-")

    project_name = get_project_name(division)
    translator_name = get_translator_name(project_name)

    edition = None
    if root_lang == 'pli':
        edition = 'ms'

    data = {
        "root": {},
        "translation": {},
        "markup": {},
        "reference": {},
        "variant_notes": {},
        "translator_comments": {},
    }

    uid = None

    for unit in po.units[1:]:
        source = unit.getsource()
        target = unit.gettarget()
        context = unit.getcontext()
        if not uid:
            uid = context.split(':')[0]

        translator_comments = {}
        variant_notes = []
        html = []
        ref = []

        for comment in unit.automaticcomments:
            comment = comment[3:]
            if comment.startswith("VAR"):
                variant_notes.append(comment[5:-1])
            else:

                if comment.startswith(HTML_PREFIX):
                    html.append(comment[len(HTML_PREFIX) :].strip("\n"))
                elif comment.startswith(REF_PREFIX):
                    ref.extend(
                        c.strip("\n") for c in comment[len(REF_PREFIX) :].split(",")
                    )
                else:
                    print(f"Markup not recognized: {file}\n\t{comment}")

        assert len(unit.othercomments) <= 1
        for comment in unit.othercomments:
            comment = comment[2:-1]
            if comment.startswith(NOTE_PREFIX):
                translator_comments[translator_name] = comment[len(NOTE_PREFIX) :]
            else:
                raise ValueError(f"Comment not recognized: {file}\n\t{comment}")

        if "" in html:
            html["~"] = html.pop("")

        assert len(html) <= 1
        if html:
            html = html[0]
        else:
            html = ""

        for var, k in {
            "source": "root",
            "target": "translation",
            "html": "markup",
            "ref": "reference",
            "variant_notes": "variant_notes"
        }.items():

            val = locals()[var]
            if (k == "root" or k == "markup") or val:
                data[k][context or "~"] = locals()[var]

        for author, comment in translator_comments.items():
            if author not in data["translator_comments"]:
                data["translator_comments"][author] = {}
            data["translator_comments"][author][context] = comment

    # verify
    data_string = json.dumps(data, indent=2, ensure_ascii=False)

    with file.open("r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):

        m = regex.search(r"#\.? (?:NOTE|HTML|VAR|REF): (.*)", line)
        if m and 'REF:' in line:
            refs = [ref.strip() for ref in m[1].split(',')]
            for ref in refs:
                if ref not in data_string:
                    print(f'Line not found: {i+1}: "{line}"')
                    break
            continue
        if not m:
            m = regex.search(r'"(.+)"', line)
        if not m:
            m = regex.search(r'((?:(?<!^)\b\w+\b[\s,.?]*)+)', line)
        if m:
            string = m[1].strip('\n')
            if json.dumps(string, ensure_ascii=False) in data_string:
                continue
            else:
                print(f'Line not found {file.name}:{i+1}: "{line}"')
                with done_file.open('w') as f:
                    json.dump(done, f)
                subprocess.run(['geany', f'{str(file)}:{i+1}'])
                raise ValueError
    
    # markup/pli/dn/dn1.json
    # root/pli/dn/dn1.json
    # translation/en/dn/dn1.json
    # reference/pli/dn/dn1.json
    # variant_notes/pli/dn/dn1.json
    # comments/pli/dn/dn1.json

    # pli/dn/dn1/dn1.root.json
    # pli/dn/dn1/dn1.translation.json
    # pli/dn/dn1/dn1.markup.json
    # pli/dn/dn1/dn1.reference.json
    # pli/dn/dn1/dn1.variant_notes.json
    # pli/dn/dn1/dn1.translator_comments.json

    # for tag in [
    #     "root",
    #     "translation",
    #     "markup",
    #     "reference",
    #     "variant_notes",
    #     "translator_comments",
    # ]:
    #     out_dir = OUT_DIR / tag / "/".join(project_dir)
    #     if not out_dir.exists():
    #         out_dir.mkdir(parents=True)
    #     out_file = out_dir / f"{file.stem}.json"

        
    #     json_dump(data[tag], f, indent=2, ensure_ascii=False)
    
    # root

    

    project_path = "/".join(project_dir)

    project_path = unzfill(project_path)

    markup_parent = OUT_DIR / "markup" / project_path
    markup_file = markup_parent / f"{uid}_markup.json"
    json_dump(data['markup'], markup_file)

    markup_html_file = markup_parent / f"{uid}_markup.html"
    html_strings = []
    for context, string in data['markup'].items():
        html_strings.append(string)
        if context != '~':
            html_strings.append(f'{{{context}}}')
    html_string = ''.join(html_strings)
    html_string = regex.sub(r'(</(p|div|blockquote|h\d)>)', r'\1\n', html_string)
    html_string = regex.sub(r'(<(p|div).*?>)', r'\n\1', html_string)
    html_string = html_string.replace('<br>', '<br>\n')
    html_string = html_string.replace('\n\n', '\n')
    text_dump(html_string, markup_html_file)

    root_parent = OUT_DIR / "root" / root_lang / edition / project_path
    root_file = root_parent / f"{uid}_root-{root_lang}-{edition}.json"
    json_dump(data['root'], root_file)
    
    translation_parent = OUT_DIR / "translation" / translation_lang / translator_name / project_path
    translation_file = translation_parent / f"{uid}_translation-{translation_lang}-{translator_name}.json"
    json_dump(data['translation'], translation_file)

    reference_parent = OUT_DIR / "reference" / project_path
    reference_file = reference_parent / f"{uid}_reference.json"
    json_dump({k:', '.join(v) for k,v in data['reference'].items()}, reference_file)

    variant_parent = OUT_DIR / "variant" / root_lang / edition / project_path
    variant_file = variant_parent / f"{uid}_variant-{root_lang}-{edition}.json"
    json_dump(data['variant_notes'], variant_file)

    comment_parent = OUT_DIR / "comment" / translator_name / project_path

    for author, comments in data["translator_comments"].items():
        comment_file = comment_parent / f"{uid}_comment-{translation_lang}-{translator_name}.json"
        json_dump(comments, comment_file)
    
    done[str(file)] = True

if done_file.exists():
    done_file.unlink()