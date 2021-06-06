HOST='http://localhost:5000'
import requests
r = requests.post(HOST+'/session/new')
data = r.json()

print(data)
