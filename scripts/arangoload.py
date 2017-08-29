
import json
import pathlib
import hashlib
import lxml.html

from collections import defaultdict, Counter

import arango
from arango import ArangoClient


import settings

conn = ArangoClient(**settings.arango)

data_dir = settings.data_dir

html_dir = data_dir / 'html_texts'
relationship_dir = data_dir / 'relationships'
structure_dir = data_dir / 'structure'

if 'sc' in conn.databases():
    conn.delete_database('sc')

db = conn.create_database('sc')

collections = [
    ('root', False),
    ('root_edges', True),
    ('html_texts', False),
    ('unicode_points', False),
    ('mtimes', False),    
    ]



for name, edge in collections:
    db.create_collection(name=name, edge=edge)


# create indexes

db['html_texts'].add_skiplist_index(fields=["uid"], unique=False)
db['html_texts'].add_skiplist_index(fields=["author_uid"], unique=False)
db['html_texts'].add_skiplist_index(fields=["lang"], unique=False)

docs = []
edges = []

mapping = {}

for root_file in sorted((structure_dir / 'division').glob('**/*.json')):
    with root_file.open('r', encoding='utf8') as f:
        entries = json.load(f)
    unique_counter = Counter(entry['_path'].split('/')[-1] for entry in entries)
    
    for i, entry in enumerate(entries):
        path = pathlib.PurePath(entry['_path'])
        mapping[path] = entry
        
        uid = path.parts[-1]
        if unique_counter[uid] > 1:
            # uid is the end of path, unless it is non-unique in which case
            # combine with the second to last part of path
            uid = '-'.join(entry['_path'].split('/')[-2:])
        
        entry['_key'] = uid
        entry['uid'] = uid
            
        del entry['_path']
        entry['num'] = i # number is used for ordering, it is not otherwise meaningful
        
        docs.append(entry)
        
        # find the parent
        parent = mapping.get(path.parent)
        if parent:
            edges.append({'_from': 'root/'+parent['_key'], '_to': 'root/'+entry['_key'], 'type': 'child'})

for category_file in sorted(structure_dir.glob('*.json')):
    category_name = category_file.stem
    collection = db.create_collection(category_name)
    category_docs = []
    
    with category_file.open('r', encoding='utf8') as f:
        entries = json.load(f)
    
    edge_type = category_file.stem
    
    for i, entry in enumerate(entries):
        entry['type'] = edge_type
        entry['_key'] = entry['uid']
        entry['num'] = i
        if 'contains' in entry:
            for uid in entry['contains']:
                child = mapping.get(pathlib.PurePath(uid))
                child[entry['type']] = entry['uid']
                edges.append({'_from': f'{category_name}/{entry["_key"]}', '_to': f'root/{child["_key"]}', 'type': edge_type})
            del entry['contains']
        category_docs.append(entry)
    collection.import_bulk(category_docs)


for entry in docs:
    if entry.get('pitaka') == 'su':
        if 'grouping' not in entry:
            entry['grouping'] = 'other'
        

# make documents
db['root'].import_bulk(docs)
db['root_edges'].import_bulk(edges)



def get_mtimes():
    # track modifications

    try:
        db.create_collection('mtimes')
    except arango.client.CollectionCreateError:
        pass

    # Extract the mtimes from arangodb

    old_mtimes = {entry['path']: entry['mtime'] for entry in db.aql.execute('''
    FOR entry in mtimes
        RETURN entry
    ''') }


    # Get the mtimes from the file system

    new_mtimes = {}
    for html_file in data_dir.glob('**/*.html'):
        new_mtimes[str(html_file.relative_to(data_dir))] = html_file.stat().st_mtime_ns

    deleted = set(old_mtimes).difference(new_mtimes)
    changed_or_new = {}

    for path, mtime in new_mtimes.items():
        if mtime != old_mtimes.get(path):
            changed_or_new[path] = mtime
    
    return changed_or_new, deleted

changed_or_new, deleted = get_mtimes()

def update_mtimes(changed_or_new, deleted):
    # Update mtimes in arangodb

    mtimes_col.aql.execute('''
    FOR entry IN mtimes
        FILTER entry.path IN @to_remove
        REMOVE entry
    ''', to_remove=list(deleted))

    db['mtimes'].import_bulk([{'path': k, 'mtime': v, '_key': k.replace('/', '_')} for k, v in changed_or_new.items()], on_duplicate="replace")

    

languages = db.aql.execute('''/* return all language objects as a key: value mapping */
    RETURN MERGE(
        FOR l IN language
            RETURN {[l.uid] : l} /* Set the key as the uid */
    )''').next()

authors = {} # to do

import textdata
with textdata.ArangoTextInfoModel(db=db) as tim:
    for lang_dir in html_dir.glob('*'):
        if not lang_dir.is_dir:
            continue
        tim.process_lang_dir(lang_dir=lang_dir, data_dir=data_dir, files_to_process=changed_or_new, force=False)
    
