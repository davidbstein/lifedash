import datetime
import time

from renderers.templates import (
    AGENDA_TEMPLATE,
    AGENDA_EVENT_LIST,
    AGENDA_ENTRY,
    PILL_COMBINED_TEMPLATE,
    PILL_TIMING_TEMPLATE,
    PILL_HISTORY_TEMPLATE,
    PILL_TIMING_CURRENT,
    PILL_TIMING_NO_CURRENT,
    PILL_TIMING_HISTORY,
    PILL_TIMING_HISTORY_ENTRY,
)

DEFAULT_PILL_SIZE = 30
PILL_TIMES = {
    '30': datetime.timedelta(hours=10),
    '25': datetime.timedelta(hours=9),
    '20': datetime.timedelta(hours=8),
    '10': datetime.timedelta(hours=2),
    'other': datetime.timedelta(hours=3),
}
def format_event_list(el):
    to_ret = []
    for e in sorted(el, key=lambda e: e['start']):
        ec = {k: v for k, v in e.items()}
        ec['start_dt'] = datetime.datetime.fromtimestamp(ec['start'])
        ec['end_dt'] = datetime.datetime.fromtimestamp(ec['end'])
        ec['age'] = ['DONE', 'STARTED', 'UPCOMING'][(time.time() < ec['start']) + (time.time() < ec['end'])]
        to_ret.append(AGENDA_ENTRY.format(**ec))
    return ''.join(to_ret)

def render_agenda(calendar_data):
    return AGENDA_TEMPLATE.format(
        today_date="{:%A, %B %d}".format(datetime.date.today()),
        tomorrow_date="{:%A, %B %d}".format(datetime.date.today() + datetime.timedelta(days=1)),
        today_events=AGENDA_EVENT_LIST.format(
            event_list=format_event_list(calendar_data.get("events", {}).get("today", []))
        ),
        tomorrow_events=AGENDA_EVENT_LIST.format(
            event_list=format_event_list(calendar_data.get("events", {}).get("tomorrow", []))
        ),
    )

def format_pill_history(pill_history):
    HISTORY_LEN = 7 * 3
    today = datetime.date.today()
    pill_ts_and_details = [(None, None) for i in range(HISTORY_LEN)]
    for pill_detail in pill_history:
        dt = datetime.datetime.fromtimestamp(pill_detail.get('timestamp'))
        days_ago = (today-dt.date()).days
        if days_ago >= HISTORY_LEN:
            continue
        pill_ts_and_details[days_ago] = (dt, pill_detail.get("pillSize", DEFAULT_PILL_SIZE))
    return PILL_TIMING_HISTORY.format(
        pill_history=''.join([
            PILL_TIMING_HISTORY_ENTRY.format(
                taken=bool(pill_time),
                taken_day=f"{pill_time:%a}"[0] + f"{pill_time:%d}" if pill_time else " ",
                taken_hour=f"{pill_time:%H:%M}" if pill_time else " ",
                taken_size=str(pill_size)
            ) for pill_time, pill_size in reversed(pill_ts_and_details)
        ])
    )

def format_timedelta(td):
    hours = (td.seconds // (60*60)) % 24
    mins = (td.seconds // 60) % 60
    return f"{hours:02}h {mins:02}m"

def get_pill_data(calendar_data):
    pill_history=sorted(calendar_data.get("pillDetail", []), key=lambda pd: pd.get("timestamp"))
    last_pill = (pill_history and pill_history[-1]) or {}
    last_pill_ts = last_pill.get("timestamp", 0)
    if not pill_history or ((time.time() - last_pill_ts) / (60*60)) > 24:
        current_pill = PILL_TIMING_NO_CURRENT
    else:
        cur_pill_start = datetime.datetime.fromtimestamp(last_pill_ts)
        cur_pill_size = str(last_pill.get("pillSize", DEFAULT_PILL_SIZE))
        cur_pill_age = datetime.datetime.now() - cur_pill_start
        cur_pill_length = PILL_TIMES.get(cur_pill_size) or datetime.timedelta(hours=10)
        current_pill = PILL_TIMING_CURRENT.format(
            current_pill_time=cur_pill_start,
            current_pill_age=format_timedelta(cur_pill_age),
            current_pill_size=cur_pill_size,
            current_pill_remaining=(cur_pill_length-cur_pill_age).total_seconds() / cur_pill_length.total_seconds()
        )
    return {
        'current_pill': current_pill,
        'pill_history': pill_history
    }
    
def render_pill_timing(calendar_data):
    return PILL_TIMING_TEMPLATE.format(
        current_pill=get_pill_data(calendar_data)['current_pill']
    )

def render_pill_history(calendar_data):
    return PILL_HISTORY_TEMPLATE.format(
        timing_history=format_pill_history(get_pill_data(calendar_data)['pill_history'])
    )

def render_pill_combined(calendar_data):
    return PILL_COMBINED_TEMPLATE.format(
        current_pill=get_pill_data(calendar_data)['current_pill'],
        timing_history=format_pill_history(get_pill_data(calendar_data)['pill_history'])
    )
