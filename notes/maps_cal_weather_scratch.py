"""
This file contains example scripts for loading different types of data.
"""

import requests
import json
import datetime
import pickle
import base64
from googleapiclient.discovery import build

with open('secrets.json') as f:
    SECRETS = json.loads(f.read())

"""
# Getting location data from Google Maps

saves `stein_data` when run, which contains example stein data:

```
{'name': 'Stein',
'photo': '<URL>',
'long': -74.0015495,
'lat': 40.7525764}
```
"""
params = {
  'authuser': 0,
  'hl': 'en',
  'gl': 'us',
  'pb': '!1m4!1m3!1i19!2i154311!3i197170!2m3!1e0!2sm!3i465169196!3m7!2sen!5e1105!12m4!1e68!2m2!1sset!2sRoadmap!4e1!5m4!1e4!8m2!1e0!1e1!6m7!1e12!2i2!26m1!4b1!39b1!44e1!50e0!23i1358902' # some arbitrary location - the statue of liberty
}
url = 'https://www.google.com/maps/preview/locationsharing/read'
cookies_dict = SECRETS['GOOGLE_MAPS_COOKIE']
resp = requests.get(url, params=params, cookies=cookies_dict).text

#TODO: if no one has shared location the response is different (it's just the final entry with no wrapping array.
# I need to test for that. Here's what a response looks like when location is shared...
resp = """)]}'
[[[["116781754423992801721","https://lh5.googleusercontent.com/-Rr_0kkLqJtg/AAAAAAAAAAI/AAAAAAAABcA/HASH_REMOVED/photo.jpg",null,"PERSON NAME",null,null,null,"0ahUKEwjquLzy2_zhAhVOTt8KHVBoCpsQvDgIFigA"]
,[null,[null,-72.0403948,31.9096785]
,1556793901539,16,"401 W 47th street, New York, NY, 10036",null,"US",-14400000]
,2,null,"0ahUKEwjquLzy2_zhAhVOTt8KHVBoCpsQu4IBCBUoEw",null,["116781754423992801721","https://lh5.googleusercontent.com/-Rr_0kkLqJtg/AAAAAAAAAAI/AAAAAAAABcA/bQgjt4sA5BA/photo.jpg","PERSON NAME","FNAME"]
,1,null,null,null,null,null,[1,100]
,1]
]
,null,"0ahUKEwjquLzy2_zhAhVOTt8KHVBoCpsQ8ZABCAE","LdHKXKruKM6c_QbQ0KnYCQ",null,null,"b64_HASH_REMOVED\u003d\u003d",4,1556795694205,[null,[null,[null,-72.029161,41.7670101]
,1556795646270,16,"300 Dodd Street, Union City, NJ 07086, USA",null,"US",-14400000]
,"IO6Lo6HGsIfHQg"]
]"""
raw_data = json.loads(resp[4:])[0]

def raw2info(data):
  lat, long = data[1][1][2], data[1][1][1]
  photo, _, name = data[0][1:4]
  return locals()

stein_data = raw2info(raw_data[0])
del stein_data['data']
print(json.dumps(stein_data, indent=' '))

"""
# # Getting weather data from HERE
"""
here_params = SECRETS['HERE_PARAMS']
here_weather_uri = "https://weather.api.here.com/weather/1.0/report.json"
params = dict(
    product="forecast_hourly",
    latitude=stein_data['lat'],
    longitude=stein_data['long'],
    **here_params
)
hourly_weather = json.loads(requests.get(here_weather_uri, params=params).text)
params = dict(
    product="forecast_7days_simple",
    latitude=stein_data['lat'],
    longitude=stein_data['long'],
    **here_params
)
daily_weather = json.loads(requests.get(here_weather_uri, params=params).text)
hourly_weather['hourlyForecasts']['forecastLocation']['forecast'][0]
def entry(e):
  f = dict(**e)
  f['comfort'] = float(e['comfort'])*1.8 + 32
  return "{weekday:>10s} {localTime:2.2}:00  -  {comfort:2.0f}  -  {description}".format(**f)
print('\n'.join(entry(e) for e in hourly_weather['hourlyForecasts']['forecastLocation']['forecast'][:6]))
hourly_weather['hourlyForecasts'].keys()

"""
# # Getting Calendar Information from google calendar
"""
google_calendar_info = SECRETS["GOOGLE_CALENDAR_INFO"]
credentials = pickle.loads(base64.b64decode(google_calendar_info['token']))
cal_service = build('calendar', 'v3', credentials=credentials)
[e['id'] for e in cal_service.calendarList().list().execute().get("items")]
now = datetime.datetime.utcnow().isoformat() + 'Z'
upcoming = cal_service.events().list(calendarId='davidbstein@gmail.com', timeMin=now,
                                        maxResults=30, singleEvents=True,
                                        orderBy='startTime').execute()
for event in upcoming['items']:
  if event['summary'].startswith("(busy on "):
    continue
  if event['start'].get('dateTime'):
    print("{time} {name}".format(
      time=event['start']['dateTime'][5:16],
      name=event['summary'],
    ))
  elif event['start'].get('date'):
    print("ALL DAY {time} {name}".format(
      time=event['start']['date'][5:16],
      name=event['summary'],
    ))
"""
# # Getting todo list from Dropbox Paper
"""
