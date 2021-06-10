#!/bin/env python
import os
import sys
from bs4 import BeautifulSoup

def getHeader(uid):
    return f'<svg e="{uid}" height="360px" id="skincolor" viewbox="0 0 360 360" width="360px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'


soup = BeautifulSoup(open(sys.argv[1]).read(), 'html.parser')
for i, svg in enumerate(soup.find_all('svg')):
    category = svg.attrs["id"]
    if not os.path.exists(category):
        os.mkdir(category)
    for asset in svg.find_all('g'):
        uid = asset.attrs.get("id", None) or asset.attrs["class"][0]
        try:
            del asset.attrs['style']
        except KeyError:
            print(f'{category}/{uid} was already visible')
        f = open(os.path.join(category, uid + ".svg"), 'w')
        f.write(getHeader(uid))
        f.write(str(asset))
        f.write('</svg>')
        f.close()

