import json
import time
import os

CACHE_DIR = "/var/tmp/.obj_store"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def _store_name(name):
    return f"{CACHE_DIR}/{name}.store"


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
    to_ret['_age'] = (time.time() - to_ret.get("last_update", 0)) / 60
    return to_ret


def save_object(name, obj):
    sn = _store_name(name)
    with open(sn, 'w') as f:
        to_dump = {'last_update': time.time()}
        to_dump.update(obj)
        json.dump(to_dump, f)
    return get_object(name)


def get_or_reload(name, reload_fn, timeout_in_minutes):
    obj = get_object(name)
    if obj.get('_age') >= timeout_in_minutes:
        to_save = reload_fn()
        obj = save_object(name, to_save)
    return obj

def get_historical(name, reload_fn, timestamp, max_age, now, obj=None):
    if timestamp < now - max_age:
        return {}
    if obj == None:
        obj = get_object(name)
    cached_vals = {ts:v for ts,v in obj.get("_values", []) if ts >= now - max_age}
    if timestamp in cached_vals.keys():
        return {"value": cached_vals[timestamp], "_obj": obj}
    print("NOTHING IN CACHE")
    cached_vals[timestamp] = reload_fn()
    obj = {"_values": list(cached_vals.items())}
    save_object(name, obj)
    return {
        "value": cached_vals[timestamp],
        "_obj": obj,
    }
        
