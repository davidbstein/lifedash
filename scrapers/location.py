import requests
import json
import time
from util import (
  get_template
)
from secrets import (
  SECRETS,
  SETTINGS,
)

_MEMOIZE = {"time": 0, "data": None}
_MEMOIZE_BUFFER_LENGTH = 30 # in seconds

_LOCATION_URL = 'https://www.google.com/maps/preview/locationsharing/read'
_SECRETS = SECRETS['GOOGLE_MAPS']
_SETTINGS = SETTINGS['GOOGLE_MAPS']


def _get_raw_map_data():
  if time.time() - _MEMOIZE['time'] < _MEMOIZE_BUFFER_LENGTH:
    return _MEMOIZE['data']
  params = {
    'authuser': 0,
    'hl': 'en',
    'gl': 'us',
    'pb': (
      '!1m7!8m6!1m3!1i14!2i8413!3i5385!2i6!3x4095'
      '!2m3!1e0!2sm!3i407105169!3m7!2sen!5e1105!12m4'
      '!1e68!2m2!1sset!2sRoadmap!4e1!5m4!1e4!8m2!1e0!'
      '1e1!6m9!1e12!2i2!26m1!4b1!30m1!'
      '1f1.3953487873077393!39b1!44e1!50e0!23i4111425' # the statue of liberty, arbitrarily.
    )
  }
  resp = requests.get(_LOCATION_URL, params=params, cookies=_SECRETS['cookie'])
  to_ret = json.loads(resp.text[4:])[0]
  _MEMOIZE['time'] = time.time()
  _MEMOIZE['data'] = to_ret
  return to_ret

def _raw2info(data):
  to_ret = {}
  to_ret['id'] = data[6][0]
  to_ret['picture_url'] = data[6][1]
  to_ret['name'] = data[6][2]
  to_ret['fname'] = data[6][3]
  to_ret['lat'] = data[1][1][2]
  to_ret['long'] = data[1][1][1]
  to_ret['ts'] = data[1][2]
  to_ret['accuracy'] = data[1][3]
  try:
      to_ret['charging'] = data[13][0]
  except:
      to_ret['charging'] = None
  try:
      to_ret['battery_level'] = data[13][1]
  except:
      to_ret['battery_level'] = None
  return to_ret

def _get_locations():
  return {
    person['id']: person
    for person in map(_raw2info, _get_raw_map_data())
    if person['id'] in _SETTINGS['ID_LIST']
  }

def get_locations_json():
  return json.dumps(_get_locations())

def get_locations_html():
  locations = _get_locations();
  template = get_template('map');
  return template.format(
    json_data=json.dumps({
      "ACCESS_TOKEN": SECRETS['MAPBOX']['public_token'],
      "ID_LIST": _SETTINGS['ID_LIST']
    })
  )

if __name__ == "__main__":
  print(json.dumps(get_friend_locations(), indent='  '))
