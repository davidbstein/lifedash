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
    return datetime.datetime.fromisoformat("{}+00:00".format(s)).astimezone(tz=dateutil.tz.tzlocal())

def _toffset(dt):
    return (dt.hour * 60 * 60 + dt.minute * 60 + dt.second) / (24 * 60 * 60)

def _doy(dt):
    doy = int(dt.strftime("%-j"))
    if doy < 30 or doy > 300:
        doy = doy + datetime.timedelta(days=180)
    return doy


def process_sleep_data(sleep_data):
    """ the output gets appended to tracker_data['timeEntries'] for the _parse_tracking_history """
    if not sleep_data:
        return []
    return [
        {
            'duration': {
                'startedAt': '2021-10-03T22:44:05.725',
                'stoppedAt': '2021-10-03T23:35:00.000'},
            'activity': {
                'color': 'black',
                'id': f'sleep-{sleep.get("sleepScores", {}).get("stress",{})}',
            },
            'note': {
                "_extra": sleep.get('sleepScores', ""),
            },
        },
        for sleep in sleep_data
    ]

#TODO: this glitches from jan 1-7 because I'm lazy.
TOP_OFFSET = 0
BOTTOM_OFFSET = 1
ATR_DICT = 2
def _parse_tracking_history(tracker_data):
    recent = tracker_data['timeEntries']
    days = [[] for _ in range(8)]
    cur = 0
    today = _doy(datetime.datetime.now())
    day_length = 24 * 60 * 60
    for te in recent:
        start = _str2dt(te['duration']['startedAt'])
        end = _str2dt(te['duration']['stoppedAt'])
        if start.day == end.day:
            days[7 - today + _doy(start)].append(
                [_toffset(start), _toffset(end), te['activity'], te['note'], te['duration']]
            )
        else:
            days[7 - today + _doy(start)].append([_toffset(start), 1, te['activity'], te['note'], te['duration']])
            days[7 - today + _doy(end)].append([0, _toffset(end), te['activity'], te['note'], te['duration']])
    activity_history_html = []
    for day in days:
        blocks = []
        for block in day:
            blocks.append(ACTIVITY_BLOCK.format(
                top=100*block[TOP_OFFSET], 
                bottom=100-(100*block[BOTTOM_OFFSET]), 
                color=block[ACTIVITY_DICT]['color'], 
                comments=json.dumps(block),
                atr_id=block[ACTIVITY_DICT]['id'],
            ))
        activity_history_html.append(ACTIVITY_DAY.format(blocks=''.join(blocks)))
    return {"activity_history_html": ''.join(activity_history_html[-7:])}


def _parse_tracking_data(data):
    track = data['currentTracking']
    if not track:
        d = {
            'activity_name': '(nothing currently tracked)'
        }
        d.update({k:"" for k in ["color", "elapsed", "note"]})
        return d
    act = track['activity']
    td = (datetime.datetime.utcnow() - dateutil.parser.isoparse(track['startedAt'])).seconds
    elapsed = "{}h:{:02d}m".format(td//3600, (td//60) & 60)
    return {
        "activity_name": "(nothing)" if not track else act['name'],
        'elapsed': elapsed,
        'color': track['activity']['color'],
        'note': track['note']['text'] or ""
    }


def render_tracker_html(activity_data):
    current_activity_data = activity_data.get("current_activity", {})
    return TRACKER_TEMPLATE.format(**_parse_tracking_data(current_activity_data))

def render_history_html(activity_data, sleep_data=None):
    recent_activity_data = activity_data.get("recent_activity", {})
    recent_activity_data['timeEntries'].extend(process_sleep_data(sleep_data))
    return ACTIVITY_TEMPLATE.format(**_parse_tracking_history(recent_activity_data))
