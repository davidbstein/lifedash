import requests
from scrapers.secrets import (
  SECRETS,
  SETTINGS,
)
from datetime import datetime, timedelta
from .caching import get_or_reload
from timeular import timeular

URI = "https://api.timeular.com/api/v3"


def get_token():
    return {"token": requests.post(URI+"/developer/sign-in", json=SECRETS['TIMEULAR']).json()['token']}

def _get_activity_dict():
    api_key = SECRETS['TIMEULAR']['apiKey']
    api_secret = SECRETS['TIMEULAR']['apiSecret']
    t = timeular.TimeularSession(api_key, api_secret, no_edit_mode=False)
    return {activity['id']: activity for activity in t.list_activities()}

def get_activity_dict():
    return get_or_reload('timeular_activity_dict', _get_activity_dict, 1500)

def endpoint_test():
    token = get_or_reload('timeular_token', get_token, 120)['token']
    headers={"Authorization": "Bearer {}".format(token)}
    return requests.get(URI+"/tracking", headers=headers)

def lookup_activity(activity_id):
    return get_activity_dict().get(activity_id, {'name': 'unknown'})

def _current_activity():
    token = get_or_reload('timeular_token', get_token, 120)['token']
    headers={"Authorization": "Bearer {}".format(token)}
    resp = requests.get(URI+"/tracking", headers=headers).json()
    if resp.get("currentTracking"):
        resp['currentTracking']['activity'] = lookup_activity(resp['currentTracking'].get('activityId'))
    return resp


def _recent_activity(days=14):
    token = get_or_reload('timeular_token', get_token, 120)['token']
    headers={"Authorization": "Bearer {}".format(token)}
    timerange = dict(
        now = str(datetime.utcnow()).replace(" ", "T")[:23],
        last_week = str(datetime.utcnow() - timedelta(days=days)).replace(" ", "T")[:23]
    )
    resp = requests.get(URI+"/time-entries/{last_week}/{now}".format(**timerange), headers=headers).json()
    for entry in resp['timeEntries']:
        act = lookup_activity(entry['activityId'])
        entry['activity'] = act
        entry.update(act)
    return resp

def _get_current_activity_data():
    return get_or_reload('current_activity', _current_activity, 0.25)


def _get_recent_activity_data():
    return get_or_reload('recent_activity', _recent_activity, 5)


def get_activity_data():
    return dict(
        current_activity=_get_current_activity_data(),
        recent_activity=_get_recent_activity_data(),
        )
