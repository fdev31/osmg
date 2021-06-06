#!/bin/env python

HOST='http://localhost:5000'
import requests
# create a new session
r = requests.post(HOST+'/session/new')
data = r.json()

print(data)

# join a session

sessionData = {
  "name": "Toto",
  "avatar": "monster",
  "sessionName": data['name']
}
r = requests.post(HOST+'/session/join', json=sessionData)

print(r.json())
