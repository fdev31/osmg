#!/bin/env python
from pprint import pprint

HOST='http://localhost:5000'
import requests

print("New session")
r = requests.post(HOST+'/session/new')
data = r.json()

pprint(data)

print("Join session")

sessionData = {
  "name": "Toto",
  "avatar": "monster",
  "sessionName": data['name']
}
r = requests.post(HOST+'/session/join', json=sessionData)

pprint(r.json())
