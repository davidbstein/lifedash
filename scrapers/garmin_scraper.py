from scrapers.secrets import (
  SECRETS,
  SETTINGS,
)
import time
import requests
from requests_oauthlib import OAuth1, OAuth1Session
from .caching import get_or_reload, get_historical


david_session = OAuth1Session(**SECRETS["GARMIN_API"]['david'])
emily_session = OAuth1Session(**SECRETS["GARMIN_API"]['emily'])

david_token = OAuth1(**SECRETS["GARMIN_API"]['david'])
emily_token = OAuth1(**SECRETS["GARMIN_API"]['emily'])

ONE_DAY = 24 * 60 * 60
__HISTORY_DAYS = 21
VALUES_KEY = "values"
WELLNESS_ENDPOINTS = [
    "activities",
    "sleeps",
    # granular daily data
    "epochs",
    "dailies",
    "bodyComps",
    "userMetrics",
    "stressDetails",
]


def history_length():
    return int(time.time()) - history_start()

def history_start():
    now = int(time.time())
    today_start = now - (now % ONE_DAY)
    return int(today_start - __HISTORY_DAYS * ONE_DAY)

def _wellness_api(endpoint, start_ts, end_ts, session, auth):
    url = f"https://apis.garmin.com/wellness-api/rest/{endpoint}"
    params={
        "uploadStartTimeInSeconds": int(start_ts),
        "uploadEndTimeInSeconds": int(end_ts)
    }
    resp = requests.get(url, params, auth=auth)
    # resp = session.get(url,params)
    values = resp.json()
    if endpoint == "dailies":
        for v in values:
            v["timeOffsetHeartRateSamples"] = {}
            del v["timeOffsetHeartRateSamples"]
            print([[k, len(str(vv))] for k, vv in v.items() if len(str(vv)) > 20])
        #values = [{"hello": 1}]
    print(values, "\n", resp.text[:500], resp.headers, resp.request)
    assert "errorMessage" not in values, values
    return {VALUES_KEY: values}


def recheck_test(cached_workouts, ts, val, age_mins):
    newer_workouts = len([_ for timestamp, _ in cached_workouts if timestamp > ts])
    workout_recorded = bool(val.get(VALUES_KEY))
    days_ago = (time.time()-ts)/(24*60*60)
    age_threshold = 120
    age_threshold *= newer_workouts + 1
    if workout_recorded:
        age_threshold *= 6
    age_threshold += 60 * days_ago
    to_ret = age_mins > age_threshold
    return to_ret #and days_ago > .5

def fill_historical(name, fn, timeout_in_minutes=24*60):
    now = int(time.time())
    start_time = history_start()
    max_age = history_length()
    step = int(ONE_DAY * .5)
    items = []
    obj=None
    reload_fn=lambda: fn(step_start, step_start+step)
    TTL_mins=24*64
    for step_start in range(start_time, now, step):
        from_cache = get_historical(
            name, reload_fn, step_start, max_age, now,
            obj=obj, recheck_test=recheck_test, TTL_mins=TTL_mins
        )
        obj = from_cache["_obj"]
        new_items= from_cache["value"].get("values", [])
        items.extend(new_items)
    latest_items = get_or_reload(
        f"{name}-current", 
        lambda: fn(now - (now % step), now),
        timeout_in_minutes
    )
    items.extend(latest_items.get(VALUES_KEY, []))
    return items

def fill_wellness_historical(endpoint, session, auth, name, timeout_in_minutes=60*24):
    try:
        return list({
            element.get("summaryId"): element
             for element in
            fill_historical(
                f"garmin/{name}-{endpoint}",
                lambda start_ts, end_ts: _wellness_api(endpoint, start_ts, end_ts, session, auth),
                timeout_in_minutes
            )
        }.values())
    except Exception as e:
        print(f"ERROR WITH {endpoint}: {e}")
        import traceback
        print(traceback.fomrat_exc())
        return []


def get_garmin_wellness_data():
    # sleeps = fill_wellness_historical("sleeps", david_session)
    if (time.time() // 60) % 100 == 0:
        print("dailies!")

    return {
        #endpoint: fill_wellness_historical(endpoint, david_session, david_token, "david")
        endpoint: fill_wellness_historical(endpoint, david_session, david_token, "david")
        for endpoint in WELLNESS_ENDPOINTS
    }
                 
def emily_get_garmin_wellness_data():
    # sleeps = fill_wellness_historical("sleeps", emily_session)
    return {
        endpoint: fill_wellness_historical(endpoint, emily_session, emily_token, "emily")
        for endpoint in WELLNESS_ENDPOINTS
    }
