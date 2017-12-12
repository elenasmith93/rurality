import requests
import json
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty

def getNPS():
    ''' Queries the National Park Service REST API to download data for all parks/protected areas '''
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
    
def getZipCoords(ZIP):
    ''' Args:
            ZIP: string ZIP code
        Returns:
            tuple coordinates  
    '''
    geolocator = Nominatim()
    location = geolocator.geocode(ZIP)

    return (location.latitude, location.longitude)

def distanceToPark(ZIP, park):
    ''' Args:
            ZIP: an integer ZIP code
            park: string representing the NPS park code
        Returns:
            distance: float distance between ZIP and park
    '''
    # get park coords
    key = 'kJvvuCY3y2UD8o7F2dlYsP1Fet6NACkeMKFG4HS0'
    base = 'https://developer.nps.gov/api/v1'
    endpoint = '/parks?'
    name = 'parkCode=%s'%park
    auth = '&limit=600&api_key=%s'%key
    resp = json.loads(requests.get(base+endpoint+name+auth).text)
    latLong = resp['data'][0]['latLong']
    
    lat = float(latLong.split('lat:')[1].split(',')[0])
    long = float(latLong.split('long:')[1])
    
    parkCoords = (lat, long)
    zipCoords = getZipCoords(ZIP)
    
    distance = vincenty(parkCoords, zipCoords).miles
    
    return distance