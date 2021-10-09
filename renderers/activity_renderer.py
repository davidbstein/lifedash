import datetime
import dateutil
import json

from renderers.templates import (
    TRACKER_TEMPLATE,
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
    if today_doy < 30 or today_doy > 300:
        dt = dt + datetime.timedelta(days=180)
    return int(dt.strftime("%-j"))


def _garmin_sleep_to_timular_entry(sleep_obj, overrides={}, id_="sleep"):
    # use mostly the same informatino, but tweak for subsections...
    sleep = {k:v for k, v in sleep_obj.items()}
    sleep.update(overrides)
    # if we use a subset, use a subset
    quality_key = {
        "sleep": "restlessness",
        "deep": "deepPercentage", 
        "light": "lightPercentage",
        "awake": "awakeCount",
        "rem": "remPercentage",
    }.get(id_, {})
    quality = sleep['sleepScores'][quality_key].get("qualifierKey", "NONE")
    # only endTime for sub-sections / only duraction for the main sleep.
    endTime = sleep.get("endTimeInSeconds", (sleep['startTimeInSeconds'] + sleep['durationInSeconds'] + sleep['awakeDurationInSeconds']))
    return {
        'duration': {
            'startedAt': _ts2timeularDate(sleep['startTimeInSeconds']),
            'stoppedAt': _ts2timeularDate(endTime),
        },
        'activity': {
            'color': '',
            'id': f'{id_}-sleep',
            '_extra_classes': [
                f'atr-sleep-quality-{quality}', 
                f'{sleep["summaryId"]}'
            ]
        },
        'note': {
            "_extra": sleep.get('sleepScores', ""),
        },
    }

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
def _parse_tracking_history(tracker_data):
    recent = tracker_data['timeEntries']
    days = [[] for _ in range(8)]
    cur = 0
    today = _doy(datetime.datetime.now())
    day_length = 24 * 60 * 60
    for te in recent:
        start = _str2dt(te['duration']['startedAt'])
        end = _str2dt(te['duration']['stoppedAt'])
        if (7 - today + _doy(start)) < 0 or (7 - today + _doy(end)) < 0:
            continue
        if start.day == end.day:
            days[7 - today + _doy(start)].append(entry_object(start, end, te))
        else:
            days[7 - today + _doy(start)].append(entry_object(start, None, te))
            days[7 - today + _doy(end)].append(entry_object(None, end, te))
    activity_history_html = []
    for day in days:
        blocks = []
        for block in day:
            blocks.append(ACTIVITY_BLOCK.format(**block))
        activity_history_html.append(ACTIVITY_DAY.format(blocks=''.join(blocks)))
    return {"activity_history_html": ''.join(activity_history_html[-7:])}


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
    return {
        "activity_name": "(nothing)" if not track else act['name'],
        'elapsed': elapsed,
        'started': started,
        'color': track['activity']['color'],
        'note': track['note']['text'] or ""
    }


def render_tracker_html(activity_data):
    current_activity_data = activity_data.get("current_activity", {})
    recent_activity_data = activity_data.get("recent_activity", {})
    return TRACKER_TEMPLATE.format(**_parse_tracking_data(current_activity_data, recent_activity_data))

def render_history_html(activity_data, sleep_data):
    recent_activity_data = activity_data.get("recent_activity", {})
    recent_activity_data['timeEntries'].extend(process_sleep_data(sleep_data))
    return ACTIVITY_TEMPLATE.format(**_parse_tracking_history(recent_activity_data))
