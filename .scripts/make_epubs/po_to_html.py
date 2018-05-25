from translate.storage.po import pofile
import lxml.html
import arango
import subprocess
import pathlib
import json
import regex

client = arango.ArangoClient(protocol='http', host='localhost', port=8529)

db = client.db('suttacentral', username='root', password='test')

storage = pathlib.Path('./storage')

subprocess.run(['docker', 'cp', 'sc-flask:/opt/sc/storage/', str(storage)], check=True)

def make_clean_html(uid):

    markup_path = storage / f'{uid}_ms.html'
    strings_path = storage / f'{uid}_sujato.json'

    markup_string = markup_path.open().read()
    strings = json.load(strings_path.open())

    def repl_fn(m):
        s = strings.get(m[1], '')
        if s:
            return s + ' '
        return s

    markup_string = regex.sub(r'<sc-seg id="([^"]+)"></sc-seg>', repl_fn, markup_string)
    markup_string = regex.sub(r' *\n *', r'\n', markup_string)
    markup_string = regex.sub(r' +', ' ', markup_string)
    root = lxml.html.fromstring(markup_string)
    for a in root.iter('a'):
        a.drop_tag()
    for p in root.iter('p'):
        tc = p.text_content()
        if not tc or tc.isspace():
            p.drop_tree()
        elif p.text:
            p.text = regex.sub(r'^\s+', '', p.text)
        
            

    string = lxml.html.tostring(root, encoding='unicode')
    string = regex.sub(r'\s+</p>', '</p>', string)
    return string