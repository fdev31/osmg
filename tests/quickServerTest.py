#!/bin/env python
import random
from pprint import pprint

HOST='http://localhost:5000'
import requests

NAME="Toto"

print("New session")
r = requests.post(HOST+'/session/new')
data = r.json()
sessionName = data['name']

pprint(data)

print("Join session")

sessionData = {
  "name": NAME,
  "avatar": "monster",
  "sessionName": sessionName
}
print(sessionData)
r = requests.post(HOST+'/session/join', json=sessionData)

session = r.json()
myId = None
for player in session['players']:
    if player['name'] == NAME:
        myId = player['id']
pprint(session)
print("My data:")
pprint(session['playersData']['P'+myId])
sessionData['id'] = myId

r = requests.post(HOST+'/game/dice/throwDice?value=4', json=sessionData)
values = r.json()
print("GOT", values)

random.shuffle(values)
print("SEND", values)

newVal = ''.join(str(x) for x in values)

r = requests.post(HOST+'/game/dice/validateDice?value='+newVal, json=sessionData)
print(r.json())


