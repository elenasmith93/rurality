import requests
import json
import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import time
import xmltodict

def getAllParks():
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

def getParkCoords(park):
    ''' Args:
            park: string NPS park code
        Returns:
            tuple coordinates  
    '''
    key = 'kJvvuCY3y2UD8o7F2dlYsP1Fet6NACkeMKFG4HS0'
    base = 'https://developer.nps.gov/api/v1'
    endpoint = '/parks?'
    name = 'parkCode=%s'%park
    auth = '&limit=600&api_key=%s'%key
    resp = json.loads(requests.get(base+endpoint+name+auth).text)
    latLong = resp['data'][0]['latLong']
    try:
        lat = float(latLong.split('lat:')[1].split(',')[0])
        long = float(latLong.split('long:')[1])
    except IndexError:
        print('API did not return coordinates for %s'%park)
        return 0
    return (lat, long)

def distanceToPark(ZIP, park, zipCoords = None):
    ''' Args:
            ZIP: an integer ZIP code
            park: string representing the NPS park code
        Returns:
            distance: float distance between ZIP and park
    '''
    parkCoords = getParkCoords(park)
    if zipCoords == None:
        zipCoords = getZipCoords(ZIP)
    
    if parkCoords != 0:
        return vincenty(parkCoords, zipCoords).miles
    else:
        return 99999

def distanceToNearestPark(ZIP):
    ''' Args:
            ZIP: an integer ZIP code
        Returns:
            Distance to nearest park
    '''
    zipCoords = getZipCoords(ZIP)
    parkCodes = list(pd.read_csv('nps.csv')['parkCode'])
    shortestDistance = 99999
    i = 0
    startTime = time.time()
    for park in parkCodes:
        distance = distanceToPark(ZIP,park, zipCoords = zipCoords)
        if distance < shortestDistance:
            shortestDistance = distance
            closestPark = park
        i += 1
        now = time.time()
        timePerIteration = (now-startTime)/i
        remainingIterations = len(parkCodes) - i
        timeRemaining = timePerIteration*remainingIterations/60
        percentDone = i/len(parkCodes)*100
        print('%f%% done; estimated time remaining: %f minutes'%(percentDone, timeRemaining))
    return closestPark, shortestDistance