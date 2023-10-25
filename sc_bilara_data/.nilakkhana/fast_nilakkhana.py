import re
import json
from hashlib import md5

from uid_to_acro import uid_to_acro

def transform(string, reference_url_pattern=None):
    """

    * -> <em>
    _ -> <i lang="pi" translate="no">
    ** -> <b>
    [label](ref) -> <a href="/ref">label</a>
    [label](https://example.com) -> <a href="https://example.com">label</a>
    [ref]() or [](ref) -> <a href="/ref">ref</a>

    reference_url_pattern:

    '/{uid}/en/sujato'
    

    Extra Rules:

    "a -> “a
    a" -> a”
    
    """


    if not reference_url_pattern:
        reference_url_pattern = '/{uid}'
    html_mapping = {}

    def subfn(m):
        result = 'TAG' + md5(m[0].encode()).hexdigest()[:20]
        html_mapping[result] = m[0]
        return result
    
    
    string = re.sub(r'<[a-z].*?>', subfn, string)

    # Rules
    string = re.sub(r'\_\_(.*?)\_\_', r'<b>\1</b>', string)
    string = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', string)

    string = re.sub(r'\*(.*?)\*', r'<em>\1</em>', string)
    string = re.sub(r'\_(.*?)\_', r"<i lang='pi' translate='no'>\1</i>", string)
    
    def link_fn(m):
        label = m[1]
        link = m[2]

        maybe_ref = (label and not link) or (link and not label)

        if label and not link:
            link = label
        if link and not label:
            label = link

        if re.match(r'https?://|#', link) or '/' in link:
            url = link
            if not label:
                label = link
        else:
            if maybe_ref:
                label = uid_to_acro(label)
            if ':' in link:
                uid, bookmark = link.split(':', 1)
            else:
                uid, bookmark = link, None

            url = reference_url_pattern.format(uid=uid)
            if bookmark:
                url = f'https://suttacentral.net{url}#{bookmark}'
            
        
        return f"<a href='{url}'>{label}</a>"
    
    string = re.sub(r'\[(.*?)\]\((.*?)\)', link_fn, string)

    def reverse_subfn(m):
        return html_mapping[m[0]]

    string = re.sub(r'TAG\w{20}', reverse_subfn, string)
    return string.lstrip()

def create_reference_url_pattern(file):
    uid, muids = file.stem.split('_')
    muids = muids.split('-')
    if muids[0] == 'comment':
        return '/'.join(['', '{uid}'] + muids[1:])
    else:
        return '/{uid}'


def process_file(file):
    reference_url_pattern = create_reference_url_pattern(file)

    print(f'For file {file.stem} using {reference_url_pattern}')
    with open(file, 'r+', encoding='utf-8') as target_file:

        data = json.load(target_file)
        target_file.seek(0)
        target_file.truncate()
        new_data = {}
        for k,v in data.items():
            new_data[k] = transform(v, reference_url_pattern)
        json.dump(new_data, target_file, indent=2, ensure_ascii=False)
