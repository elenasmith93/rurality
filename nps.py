import requests
import json
import pandas as pd

key = 'kJvvuCY3y2UD8o7F2dlYsP1Fet6NACkeMKFG4HS0'

base = 'https://developer.nps.gov/api/v1'
endpoint = '/parks?'
name = '/parkCode'
auth = '&limit=600&api_key=%s'%key
resp = json.loads(requests.get(base+endpoint+name+auth).text)

cols = list(resp['data'][0].keys())
df = pd.DataFrame(index = [], columns = cols)
for i in range(len(resp['data'])):
    for col in cols:
        df.loc[i, col] = resp['data'][i][col]
        
df.to_csv('nps.csv')
    