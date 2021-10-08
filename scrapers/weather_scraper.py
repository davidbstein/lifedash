import requests
from .caching import get_or_reload
OWM_API_ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

def _load_weather():
    resp = requests.get(OWM_API_ENDPOINT,
                       params={
                            'lat':40.7391908,
                            'lon':-74.0055301,
                            'appid':"1554269d0bb0596f535402f0225c4c6c",
                            'units': 'imperial',
                        })
    return resp.json()

def get_weather_data():
    to_ret = get_or_reload('weather', _load_weather, 15)
    if to_ret.get('daily'):
        return to_ret
    return None
