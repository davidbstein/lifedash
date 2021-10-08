from scrapers.secrets import (
  SECRETS,
  SETTINGS,
)
import time
from requests_oauthlib import OAuth1Session
from .caching import get_or_reload, get_historical


SECRETS['GARMIN_API']

session = OAuth1Session(**SECRETS["GARMIN_API"])

ONE_DAY = 24 * 60 * 60
__HISTORY_DAYS = 2
VALUES_KEY = "values"
WELLNESS_ENDPOINTS = [
    "activities",
    "sleeps",
    # granular daily data
    "epochs",
    "dailies",
    "bodyComps",
    "userMetrics"
]


def history_length():
    return int(time.time()) - history_start()

def history_start():
    now = int(time.time())
    today_start = now - (now % ONE_DAY)
    return today_start - __HISTORY_DAYS * ONE_DAY

def _wellness_api(endpoint, start_ts, end_ts):
    resp = session.get(
        f"https://apis.garmin.com/wellness-api/rest/{endpoint}",
        params={
            "uploadStartTimeInSeconds": int(start_ts),
            "uploadEndTimeInSeconds": int(end_ts)
        }
    )
    values = resp.json()
    return {VALUES_KEY: values}



# 8 hour chunks
def get_current(fn):
    pass

def fill_historical(name, fn, timeout_in_minutes=60):
    now = int(time.time())
    start_time = history_start()
    max_age = history_length()
    step = ONE_DAY // 8
    items = []
    for step_start in range(start_time, now, step):
        new_items = get_historical(
            name, 
            lambda: fn(step_start, step_start+step),
            step_start,
            max_age,
            now,
        )
        new_items = new_items.get("values", [])
        items.extend(new_items)
    latest_items = get_or_reload(
        f"{name}-current", 
        lambda: fn(now - (now % step), now),
        timeout_in_minutes
    )
    items.extend(latest_items.get(VALUES_KEY, []))
    return items

def fill_wellness_historical(endpoint, timeout_in_minutes=60):
    return fill_historical(
        f"garmin-{endpoint}",
        lambda start_ts, end_ts: _wellness_api(endpoint, start_ts, end_ts),
        timeout_in_minutes
    )

def get_garmin_wellness_data():
    sleeps = fill_wellness_historical("sleeps")
    return {
        endpoint: fill_wellness_historical(endpoint) for endpoint in WELLNESS_ENDPOINTS
    }
                 