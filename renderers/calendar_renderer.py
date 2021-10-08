import datetime
import time

from renderers.templates import (
    AGENDA_TEMPLATE,
    AGENDA_EVENT_LIST,
    AGENDA_ENTRY,
    PILL_TIMING_TEMPLATE,
    PILL_TIMING_CURRENT,
    PILL_TIMING_NO_CURRENT,
    PILL_TIMING_HISTORY,
    PILL_TIMING_HISTORY_ENTRY,
)

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
    HISTORY_LEN = 14
    today = datetime.date.today()
    pill_times = [None for i in range(HISTORY_LEN)]
    for pill_ts in pill_history:
        dt = datetime.datetime.fromtimestamp(pill_ts)
        days_ago = (today-dt.date()).days
        if days_ago >= HISTORY_LEN:
            continue
        pill_times[days_ago] = dt
    return PILL_TIMING_HISTORY.format(
        pill_history=''.join([
            PILL_TIMING_HISTORY_ENTRY.format(
                taken=bool(pill_time),
                taken_day=f"{pill_time:%a}"[0] + f"{pill_time:%d}" if pill_time else " ",
                taken_hour=f"{pill_time:%H:%M}" if pill_time else " "
            ) for pill_time in reversed(pill_times)
        ])
    )

def format_timedelta(td):
    hours = (td.seconds // (60*60)) % 24
    mins = (td.seconds // 60) % 60
    return f"{hours:02}:{mins:02}"

def render_pill_timing(calendar_data):
    pill_ts_list=sorted(calendar_data.get("events", {}).get("pills", []))
    if not pill_ts_list or ((time.time() - pill_ts_list[-1]) / (60*60)) > 12:
        current_pill = PILL_TIMING_NO_CURRENT
    else:
        cur_pill_start = datetime.datetime.fromtimestamp(pill_ts_list[-1])
        current_pill = PILL_TIMING_CURRENT.format(
            current_pill_time=cur_pill_start,
            current_pill_age=format_timedelta(datetime.datetime.now() - cur_pill_start)
        )
    return PILL_TIMING_TEMPLATE.format(
        current_pill=current_pill,
        timing_history=format_pill_history(pill_ts_list)
    )
