#!/bin/env python
import os

data = {}

OPTIONAL = set(['tattoos', 'glasses', 'facialhairs', 'accesories'])

for root, dirs, files in os.walk(os.path.curdir):
    if root == os.path.curdir:
        continue
    d = data[root[2:]] = []
    pfx = root[2] + '_'
    for fname in files:
        if fname.endswith('.svg'):
            try:
                d.append(fname.split('_', 1)[1][:-4])
            except IndexError:
                pass

data['hairstyles'] = list(set(data['hair_front'] + data['hair_back']))
del data['hair_front']
del data['hair_back']

for k, v in sorted(data.items()):
    if v:
        if k in OPTIONAL:
            tmp = []
            for name in list(v):
                tmp.extend([name, 'none'])
            v = tmp
        print("const %s = %r;"%(k, list(sorted(v))))
