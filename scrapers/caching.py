import json
import time
import os

CACHE_DIR = "/var/tmp/.obj_store"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def _store_name(name):
    dirpath = CACHE_DIR
    if "/" in name:
        dirpath = f"{CACHE_DIR}/{''.join(name.split('/')[:-1])}"
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)        
    return f"{CACHE_DIR}/{name}.store"


def _ts_to_age_mins(ts):
    return (time.time() - ts) / 60

def get_object(name):
    sn = _store_name(name)
    if not os.path.exists(sn):
        with open(sn, 'w') as f:
            json.dump({"last_update": 0}, f)
    with open(sn, 'r') as f:
        try:
            to_ret = json.load(f)
        except:
            with open(sn, 'w') as f:
                json.dump({"last_update": 0}, f)
                to_ret = {"last_update": 0}
    to_ret['_age'] = _ts_to_age_mins(to_ret.get("last_update", 0))
    return to_ret


def save_object(name, obj):
    sn = _store_name(name)
    with open(sn, 'w') as f:
        to_dump = {'last_update': time.time()}
        to_dump.update(obj)
        json.dump(to_dump, f)
    return get_object(name)


def get_or_reload(name, reload_fn, timeout_in_minutes):
    # reload_fn MUST return a dictionary
    obj = get_object(name)
    if obj.get('_age', timeout_in_minutes+10) >= timeout_in_minutes:
        to_save = reload_fn()
        obj = save_object(name, to_save)
    return obj


def get_historical(
        name, reload_fn, timestamp, max_age, now,
        obj=None, TTL_mins=24*60, recheck_test=lambda *_, **__: False
    ):
    '''
    Function to see if an entry exists in cache <name> at time <timestamp>.
    
      - looks up a cached list <name>, which contains a list of historical results.
        - if there is no cached object, make a new one.
        - _values are [ts, value] tuples
          - value is a dict {"_value": dict, "_ts": int}
        - [ts] > max_age triggers a reset.
      - if obj._values.[timestamp] is undefined, call <reload_fn>
    '''
    if timestamp < now - max_age:
        return {}
    if obj == None:
        obj = get_object(name)
    if '_age' not in obj:
        print(f"expected object to have key '_age'. keys: {obj.keys()}. Overriding!")
        obj = dict(obj.items())
        obj['_age'] = _ts_to_age_mins(max(v['_ts'] for ts, v in obj['_values']))
    if obj['_age'] > TTL_mins:
        print(obj.keys())
        print(f"TTL exceeded: {obj.get('_age')} > {TTL_mins}")
        obj.update({'_values': [], 'last_update': 0})

    cached_vals = {ts:v for ts,v in obj.get("_values", []) if ts >= now - max_age}
    if timestamp in cached_vals.keys():
        cached_workouts = [[ts, val["_value"].get("values")] for ts, val in cached_vals.items() if val['_value'].get("values")]
        if recheck_test(cached_workouts, timestamp, cached_vals[timestamp]['_value'], _ts_to_age_mins(cached_vals[timestamp]['_ts'])):
            print("reloading empty ts", timestamp)
            cached_vals[timestamp] = {"_value": reload_fn(), "_ts": time.time()}
            obj = {"_values": list(cached_vals.items())}
    else:
        print(f"NOTHING IN CACHE: {name}")
        cached_vals[timestamp] = {"_value": reload_fn(), "_ts": time.time()}
        obj = {"_values": list(cached_vals.items())}
    save_object(name, obj)
    return {
        "value": cached_vals[timestamp]["_value"],
        "_obj": obj, # this will get passed back in looping calls as params.obj
    }
        
