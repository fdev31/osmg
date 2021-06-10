#!/bin/env python
import os
import sys
from bs4 import BeautifulSoup

def getHeader(uid):
    return f'<svg e="{uid}" height="360px" id="skincolor" viewbox="0 0 360 360" width="360px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'

svg_fragments = []

def digestSVG(data, visible=True):
    if visible:
        print('<g class="h_longhair" style="display:none;">')
    else:
        print('<g class="h_longhair">')
    soup = BeautifulSoup(data, 'html.parser')
    for i, svg in enumerate(soup.find('svg')): # expect 1
        print(''.join(str(x) for x in svg.contents))
    assert i == 0
    print('</g>')

for root, dirs, files in os.walk('.'):
    if root == '.':
        continue
    print(getHeader(root))
    for fname in files:
        digestSVG(
                open(os.path.join(root, fname)).read(),
                visible = 'default' in fname
                )
    print('</svg>')
