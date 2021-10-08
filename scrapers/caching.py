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

def get_historical(name, reload_fn, timestamp, max_age, now):
    timestamp_age = now - timestamp
    if timestamp_age > max_age:
        return {}
    obj = get_object(name)
    cur_values = obj.get("_value", [])
    final_values = []
    timestamp_found = False
    for capture_time, value in cur_values:
        cur_age = now - capture_time
        if cur_age > max_age:
            continue
        if capture_time == timestamp:
            return value
        if (capture_time > timestamp) and not timestamp_found:
            to_ret = reload_fn()
            final_values.append([timestamp, to_ret])
            timestamp_found = True
        final_values.append([capture_time, value])
    if not timestamp_found:
        to_ret = reload_fn()
        final_values.append([timestamp, to_ret])
    save_object(name, {"_value": list(sorted(final_values))})
    return to_ret