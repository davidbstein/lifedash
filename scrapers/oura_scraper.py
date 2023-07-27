from scrapers.secrets import (
  SECRETS,
  SETTINGS,
)
import json
import time
import datetime
from .caching import get_or_reload

import requests 
BASE_V1 = 'https://api.ouraring.com/v1'
BASE_V2 = 'https://api.ouraring.com/v2/usercollection'
DAVID_TOKEN = SECRETS['OURA']['david_token']
EMILY_TOKEN = SECRETS['OURA']['emily_token']
ONE_DAY = datetime.timedelta(days=1)

def _iso_to_timestamp(iso_dt_string):
    return int(datetime.datetime.fromisoformat(iso_dt_string).timestamp())

def _oura_get(url, params, method, endpoint, token):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        print(f'scrape oura - (getting {url})')
        resp = requests.request(method, url, headers=headers, params=params)
        assert resp.status_code == 200, f"{url} - {params} - {resp} - {resp.text}"
        to_ret = resp.json()
        assert not to_ret.get('next_token'), to_ret
        return to_ret
    except Exception as e:
        print(e)
        return {}

def _oura_v1_get(endpoint, dt, token, method="GET"):
    params = { 
        'start': str(dt.date() - ONE_DAY),
        'end': str(dt.date() + (ONE_DAY)),
    }
    return _oura_get(f"{BASE_V1}/{endpoint}", params, method, endpoint, token)

def _oura_v2_get(endpoint, params, token, method="GET"):
    return _oura_get(f"{BASE_V2}/{endpoint}", params, method, endpoint, token)

def get_heartrate_for_day(dt, token):
    params = {'end_datetime': dt.strftime("%Y-%m-%dT%H:%M:%S%z")}
    resp = _oura_v2_get("heartrate", params, token)
    return resp

def get_activity_for_day(dt, token):
    resp = _oura_v1_get("activity", dt, token)
    return resp

def get_sleep_for_day(dt, token):
    resp = _oura_v1_get("sleep", dt, token)
    sleeps = resp['sleep']
    for sleep in sleeps:
        sleep['bedtime_end'] = _iso_to_timestamp(sleep['bedtime_end'])
        sleep['bedtime_start'] = _iso_to_timestamp(sleep['bedtime_start'])
    return {"sleep": sleeps}
    
def get_readiness_for_day(dt, token):
    resp = _oura_v1_get("readiness", dt, token)
    return resp

def get_range(name, fn, end, token, days_back=22, label="david", oura_key=None):
    if oura_key is None:
        oura_key = name
    to_ret_raw = []
    for days_ago in range(days_back):
        current = end - datetime.timedelta(days=days_ago)
        try:
            timeout = 60 * 8
            val = get_or_reload(
                f"oura/{label}-{name}-{days_ago}_days_ago",
                lambda: fn(current, token), timeout)
            if (time.time() - val.get("bedtime_end", time.time()) > 60*60*20):
                if (days_ago <= 1):
                    timeout = 1
                val = get_or_reload(
                    f"oura/{label}-{name}-{days_ago}_days_ago",
                    lambda: fn(current, token), timeout)                    
            to_ret_raw.append(
                val
            )
        except Exception as e:
            raise(e)
    to_ret_raw = sum((e[oura_key] for e in reversed(to_ret_raw) if oura_key in e), [])
    seen = set()
    to_ret = []
    for entry in to_ret_raw:
        hash_ = ''.join(sorted(json.dumps(entry)))
        if hash_ in seen:
            continue
        seen.add(hash_)
        to_ret.append(entry)
    return to_ret

def get_oura_data():
    today = datetime.datetime.now()
    start = today - datetime.timedelta(days=3)
    token = DAVID_TOKEN
    return {
        "sleep": get_range('sleep', get_sleep_for_day, today, token),
        "activity": get_range('activity', get_activity_for_day, today, token),
        "heartrate": get_range('heartrate', get_heartrate_for_day, today, token, oura_key="data"),
        "readiness": get_range('readiness', get_readiness_for_day, today, token),
    }

def emily_get_oura_data():
    today = datetime.datetime.now()
    start = today - datetime.timedelta(days=3)
    token = EMILY_TOKEN
    return {
        "sleep": get_range('sleep', get_sleep_for_day, today, token, label="emily"),
        "activity": get_range('activity', get_activity_for_day, today, token, label="emily"),
        "heartrate": get_range('heartrate', get_heartrate_for_day, today, token, label="emily"),
        "readiness": get_range('readiness', get_readiness_for_day, today, token, label="emily"),
    }
