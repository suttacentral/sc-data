
import json
import pathlib

from collections import defaultdict, Counter

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
    ('root_edges', True)
    ]

for name, edge in collections:
    db.create_collection(name=name, edge=edge)

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
