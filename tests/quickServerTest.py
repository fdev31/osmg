#!/bin/env python
import random
from pprint import pprint

HOST='http://localhost:5000'
import requests

NAME="Toto"

print("New session")
r = requests.post(HOST+'/session/new')
sessionData = r.json()

pprint(sessionData)

print("Join session")

userData = {
  "name": NAME,
  "avatar": "monster",
  "sessionName": sessionData['name']
}
r = requests.post(HOST+'/session/join', json=userData)
session = r.json()
myId = None
for player in session['players']:
    if player['name'] == NAME:
        myId = player['id']
pprint(session)
print("My data:")
#pprint(session['playersData']['P'+myId])
playerIdentifier = {
        'id': myId,
        'sessionName': sessionData['name'],
        'secret': session['secret']
        }
pprint(session)
r = requests.post(HOST+'/session/start', json=playerIdentifier)
print("STARTED", r.json())

r = requests.post(HOST+'/game/marathon/throwDice?value=4', json=playerIdentifier)
values = r.json()
print("GOT", values)

random.shuffle(values)
print("SEND", values)

newVal = ''.join(str(x) for x in values)

r = requests.post(HOST+'/game/marathon/validateDice?value='+newVal, json=playerIdentifier)
print(r.json())


