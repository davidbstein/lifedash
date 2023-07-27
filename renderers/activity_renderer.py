import datetime
import dateutil
import json
import time


from renderers.templates import (
    TRACKER_TEMPLATE,
    TRACKER_TIMEULAR_TAG,
    ACTIVITY_TEMPLATE,
    ACTIVITY_BLOCK,
    ACTIVITY_DAY,
)

def _str2dt(s):
    if len(s) >= len("YYYY-MM-ddTHH:MM:SS-TZ:TZ"):
        return datetime.datetime.fromisoformat(s).astimezone(tz=dateutil.tz.tzlocal())
    return datetime.datetime.fromisoformat("{}+00:00".format(s)).astimezone(tz=dateutil.tz.tzlocal())

def _toffset(dt):
    return (dt.hour * 60 * 60 + dt.minute * 60 + dt.second) / (24 * 60 * 60)

def _ts2timeularDate(ts):
    return f"{datetime.datetime.fromtimestamp(ts).astimezone(tz=dateutil.tz.tzlocal()).isoformat()}"

def _doy(dt):
    if not dt:
        return None
    today_doy = int(datetime.datetime.now().strftime("%-j"))
    if today_doy < 60 or today_doy > 270:
        dt = dt + datetime.timedelta(days=180)
    return int(dt.strftime("%-j"))


def _pill_to_timular_entry(pill_entry, id_="pill"):
    #print(json.dumps(pill_entry, indent=2))
    HOURS = 60*60
    size = str(pill_entry.get("pillSize", 30)).upper()
    duration = {
        "30": 10*HOURS,
        "25": 8*HOURS,
        "20": 7*HOURS,
        "10": 2*HOURS,
        "OTHER": 3 * HOURS,
    }[size]
    return {
        'duration': {
            'startedAt': _ts2timeularDate(pill_entry['timestamp']),
            'stoppedAt': _ts2timeularDate(pill_entry['timestamp'] + duration),
        },
        'activity': {
            'color': '',
            'id': f'{id_}-pill',
            '_extra_classes': [
                f'atr-pill-size-{size}', 
            ]
        },
        'note': {
            "_full_data": pill_entry
        },
    }

def _oura_sleep_to_timeular_entry(sleep_entry, id_="sleep"):
    #print(json.dumps(sleep_entry['bedtime_start'], indent=2))
    score = sleep_entry.get("score", 0)
    quality = ["POOR", "FAIR", "GOOD", "EXCELLENT"][(score > 50) + (score > 67) + (score > 80)]
    return {
        'duration': {
            'startedAt': _ts2timeularDate(sleep_entry['bedtime_start']),
            'stoppedAt': _ts2timeularDate(sleep_entry['bedtime_end']),
        },
        'activity': {
            'color': '',
            'id': f'{id_}-sleep',
            '_extra_classes': [
                f'atr-sleep-quality-{quality}', 
            ]
        },
        'note': {
            "_scores": {key:sleep_entry[key] for key in sleep_entry.keys() if 'score' in key},
            "_full_data": sleep_entry
        },
    }
    
def _garmin_workout_to_timeular_entry(workout_entry, id_="workout"):
    return {
        'duration': {
            'startedAt': _ts2timeularDate(workout_entry['startTimeInSeconds']),
            'stoppedAt': _ts2timeularDate(workout_entry['startTimeInSeconds']+workout_entry['durationInSeconds']),
        },
        'activity': {
            'color': '',
            'id': f'{id_}-workout',
            '_extra_classes': [
                f'atr-workout-{workout_entry["activityType"]}', 
            ]
        },
        'note': {
            "_full_data": workout_entry
        },
    }

def _current_timeular_to_timeular_record(current_activity):
    #print(current_activity)
    now = _ts2timeularDate(int(time.time()))
    to_ret = [
        {
            'duration': {
                'startedAt': now,
                'stoppedAt': now,
            },
            'activity': {
                'color': '',
                'id': f'atr-now-line',
                '_extra_classes': [f'atr-now']        
            },
            "note": {}
        }
    ]
    if current_activity.get('currentTracking'):
        to_ret.append(
            {
                'duration': {
                    'startedAt': current_activity['currentTracking']['startedAt'],
                    'stoppedAt': now,
                },
                'activity': dict(
                    _extra_classes=[f'atr-current'],
                    **current_activity['currentTracking']['activity']
                ),
                'note': {},
            }
        )
    return to_ret


def process_sleep_data(sleep_data):
    """ the output gets appended to tracker_data['timeEntries'] for the _parse_tracking_history """
    if not sleep_data:
        return []
    sleep_data_as_timeular = []
    for sleep in sleep_data:
        sleep_data_as_timeular.append(_garmin_sleep_to_timular_entry(sleep))
        for sleep_type in sleep.get('sleepLevelsMap', {}).keys():
            #SLEEP_TYPES = ["deep", "light", "awake", "rem"]
            sleep_data_as_timeular.extend([
                _garmin_sleep_to_timular_entry(sleep, overrides, id_=sleep_type)
                for overrides in sleep.get('sleepLevelsMap', {}).get(sleep_type)
            ])
    # print(json.dumps(sleep_data_as_timeular, indent=' '))
    return sleep_data_as_timeular

def entry_object(start, end, te):
    top_offset = _toffset(start) if start else 0
    bottom_offset = _toffset(end) if end else 1
    return dict(
        top=100 * top_offset,
        bottom=100 - ( 100 * bottom_offset ),
        color=te['activity']['color'],
        comments=[_doy(start), start, top_offset, _doy(end), end, bottom_offset, te],
        atr_id=f'{te["activity"]["id"]} {" ".join(te["activity"].get("_extra_classes", []))}'
    )

#TODO: this glitches from jan 1-7 because I'm lazy.
TOP_OFFSET = 0
BOTTOM_OFFSET = 1
ACTIVITY_DICT = 2
NUM_DAYS = 14
def _parse_tracking_history(tracker_data):
    recent = tracker_data['timeEntries']
    days = [[] for _ in range(NUM_DAYS+1)]
    cur = 0
    today_dt = datetime.datetime.now()
    today = _doy(datetime.datetime.now())
    day_length = 24 * 60 * 60
    for te in recent:
        start = _str2dt(te['duration']['startedAt'])
        end = _str2dt(te['duration']['stoppedAt'])
        if (NUM_DAYS - today + _doy(start)) < 0 or (NUM_DAYS - today + _doy(end)) < 0:
            continue
        if start.day == end.day:
            days[NUM_DAYS - today + _doy(start)].append(entry_object(start, end, te))
        else:
            days[NUM_DAYS - today + _doy(start)].append(entry_object(start, None, te))
            days[NUM_DAYS - today + _doy(end)].append(entry_object(None, end, te))
    activity_history_html = []
    for day in days:
        blocks = []
        for block in day:
            blocks.append(ACTIVITY_BLOCK.format(**block))
        activity_history_html.append(ACTIVITY_DAY.format(blocks=''.join(blocks)))
    return {"activity_history_html": ''.join(activity_history_html[-NUM_DAYS:])}


def _parse_note(note, bgcolor):
    text = note['text'] or ""
    for tag in note.get("tags", []):
        key = "<{{|t|"+f"{tag['id']}"+"|}}>"
        text = text.replace(key, TRACKER_TIMEULAR_TAG.format(bgcolor=bgcolor, **tag))
    return text

def _parse_tracking_data(data, history=None):
    track = data['currentTracking']
    if not track:
        if history and history.get('timeEntries'):
            last_activity=list(sorted(
                history.get('timeEntries'), 
                key=lambda e: e.get('duration', {}).get("stoppedAt")
            ))[-1]
            started=_str2dt(last_activity['duration']['stoppedAt'])
            td = (datetime.datetime.now().astimezone(tz=dateutil.tz.tzlocal()) - started).seconds
            elapsed = "{}h:{:02d}m".format(td//3600, (td//60) & 60)
        return {
            'activity_name': '(nothing currently tracked)',
            'elapsed': elapsed,
            'started': started,
            'color': "",
            'note': "",
        }
    act = track['activity']
    started = dateutil.parser.isoparse(track['startedAt'])
    td = (datetime.datetime.utcnow() - started).seconds
    elapsed = "{}h:{:02d}m".format(td//3600, (td//60) & 60)
    color = track['activity']['color']
    return {
        "activity_name": "(nothing)" if not track else act['name'],
        'elapsed': elapsed,
        'started': started,
        'color': color,
        'note': _parse_note(track['note'], color)
    }

def render_tracker_html(activity_data):
    current_activity_data = activity_data.get("current_activity", {})
    recent_activity_data = activity_data.get("recent_activity", {})
    return TRACKER_TEMPLATE.format(**_parse_tracking_data(current_activity_data, recent_activity_data))

def render_history_html(activity_data, oura_sleep_data, garmin_data=None, calendar_data=None):
    #recent_activity_data['timeEntries'].extend(process_sleep_data(sleep_data))
    recent_activity_data = activity_data.get("recent_activity", {})
    recent_activity_data['timeEntries'].extend(map(_oura_sleep_to_timeular_entry, oura_sleep_data))
    current_activity_data = activity_data.get("current_activity", {})
    recent_activity_data['timeEntries'].extend(_current_timeular_to_timeular_record(current_activity_data))
    if calendar_data:
        pills = calendar_data.get('pillDetail')
        recent_activity_data['timeEntries'].extend(map(_pill_to_timular_entry, pills))
    if garmin_data:
        recent_activity_data['timeEntries'].extend(map(_garmin_workout_to_timeular_entry, garmin_data['activities']))
    return ACTIVITY_TEMPLATE.format(**_parse_tracking_history(recent_activity_data))
