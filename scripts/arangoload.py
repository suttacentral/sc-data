
import json
import pathlib

from collections import defaultdict, Counter

from pyArango.connection import *
from pyArango.collection import Collection, Field, Edges
from pyArango.graph import Graph, EdgeDefinition

import settings

conn = Connection(**settings.arango)
db = conn.databases['sc']

data_dir = settings.data_dir

html_dir = data_dir / 'html_texts'
relationship_dir = data_dir / 'relationships'
structure_dir = data_dir / 'structure'


collections = [
    ('Collection', 'division'),
    ('Edges', 'division_edges'),
    ('Collection', 'categories')
    ]


for class_name, name in collections:
    if not name in db.collections:
        db.createCollection(class_name, name=name)
    else:
        db[name].empty()

docs = []
category_docs = []
edges = []

mapping = {}

for division_file in sorted((structure_dir / 'division').glob('**/*.json')):
    with division_file.open('r', encoding='utf8') as f:
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
            edges.append({'_from': 'division/'+parent['_key'], '_to': 'division/'+entry['_key']})


for category_file in sorted(structure_dir.glob('*.json')):
    with category_file.open('r', encoding='utf8') as f:
        entries = json.load(f)
    
    edge_type = category_file.stem
    
    for i, entry in enumerate(entries):
        entry['type'] = edge_type
        entry['_key'] = entry['uid']
        entry['num'] = i
        
        category_docs.append(entry)
        for uid in entry['contains']:
            child = mapping.get(pathlib.PurePath(uid))
            edges.append({'_from': 'categories/'+entry['_key'], '_to': 'division/'+child['_key'], 'type': edge_type})

# make documents
db['division'].importBulk(docs)
db['categories'].importBulk(category_docs)
db['division_edges'].importBulk(edges)

            
        
        
        

