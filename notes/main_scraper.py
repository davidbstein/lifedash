#!/usr/bin/env python
# coding: utf-8

# # Preload weather data

# In[2]:


import json, datetime, time
import requests

from os import path

def _store_name(name):
    return ".obj_store/{}.store".format(name)

def get_object(name):
    sn = _store_name(name)
    if not path.exists(sn):
        with open(sn, 'w') as f:
            json.dump({"last_update": 0}, f)
    with open(sn, 'r') as f:
        to_ret = json.load(f)
    to_ret['_age'] = (time.time() - to_ret.get("last_update", 0)) // 60
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
        obj = save_object(name, reload_fn())
    return obj

def load_weather():
    print("loading weather from openweathermap")
    resp = requests.get("https://api.openweathermap.org/data/2.5/onecall",
                        params={
                            'lat':40.7391908,
                            'lon':-74.0055301,
                            'appid':"1554269d0bb0596f535402f0225c4c6c",
                            'units': 'imperial',
                        })
    return resp.json()
weather = get_or_reload('weather', load_weather, 15)

def _ts2hour(ts):
    return datetime.datetime.fromtimestamp(ts).hour

def _ts2time(ts):
    return "{}:{}".format(datetime.datetime.fromtimestamp(ts).hour, datetime.datetime.fromtimestamp(ts).minute)


# In[3]:


HTML_TEMPLATE = """
<html>
<head>
<link rel="stylesheet" href="/css/chrome.css" type="text/css" />
</head>
<body class="hour-{hour}" style="background-image: url('/img/bgs/hours/bg{hour}.jpg')">
{content}
</pre>
</div>
</body>
</html>
"""
FIELD_TEMPLATE = """
<div id='{field}' class='fieldbox'>
    <div class="field-title">
        <h1> {title} </h1>
    </div>
    <div class='field-content'>
        {data}
    </div>
</div>
"""

FIELDBOX_TEMPLATE = """
<div id='{field}' class='fieldbox'>
    {html}
</div>
"""

def render(field, raw_data):
    if not raw_data.get('html'):
        return FIELD_TEMPLATE.format(field=field, data=raw_data['data'], title=raw_data['title'])
    return FIELDBOX_TEMPLATE.format(field=field, html=raw_data['html'])

import json, datetime
def clear_www():
    with open("/home/pi/lifedash/www/raw.json", 'w') as f:
        f.write("{}")

def write_to_www(field, data, html="", title=None):
    with open("/home/pi/lifedash/www/raw.json", 'r') as f:
        page_data = json.loads(f.read())
    cur_time = str(datetime.datetime.now())
    page_data.update({field: {'data': data, 'html': html, 'ts': 0, "title": title or field}, "last_update": {"data": cur_time, "title": "Last Update"}})
    with open("/home/pi/lifedash/www/raw.json", 'w') as f:
        f.write(json.dumps(page_data))
    update_www()
    
def update_www():
    with open("/home/pi/lifedash/www/raw.json", 'r') as f:
        page_data = json.loads(f.read())
    with open("/home/pi/lifedash/www/index.html", 'w') as f:
        content = ''.join(render(f,d) for f, d in page_data.items())
        f.write(HTML_TEMPLATE.format(content=content, hour=datetime.datetime.now().hour))
update_www()


# # Weather

# In[2]:


if weather.get('daily'):
    def get_weather_icon(icon_str):
        # dont return "http://openweathermap.org/img/wn/{}@2x.png".format(icon_str)
        return "/img/weather/{}.png".format(icon_str)

    WEEKLY_FORCAST = """
    <div class='weekly-forcast-entry'>
        {daily_entries}
    </div>
    """
    DAILY_FORCAST = """
    <div class='daily-weather-entry'>
        <div class='dwe-high'>{high:.0f}&deg</div>
        <div class='dwe-icon'><img src="{icon}" /></div>
        <div class='dwe-low'>{low:.0f}&deg</div>
        <div class='dwe-dow'>{dow:.2}</div>
    </div>
    """

    def gen_day_entry(data):
        to_ret = {k:v for k, v in data.items()}
        to_ret.update({
            'dow': datetime.date.fromtimestamp(data['dt']).strftime("%a"),
            'icon': get_weather_icon(data['weather'][0]['icon']),
            'low': data['temp']['min'],
            'high': data['temp']['max'],
        })
        to_ret['html'] = DAILY_FORCAST.format(**to_ret)
        return to_ret

    def daily(data):
        disp_data = [gen_day_entry(d) for d in data[1:8]]
        return {
            'daily_entries': ''.join(d['html'] for d in disp_data)
        }
    write_to_www('weekly-weather', weather, html=WEEKLY_FORCAST.format(**daily(weather['daily'])), title="Daily Weather")


    WEATHER_TEMPLATE = """
    <div id="w-sun">
        {sun_info}
    </div>
    <div id="w-daily">
        {daily}
    </div>
    """

    CURRENT_TEMPLATE = """
    <div class='cur-stats'>
        <div class='cur-temp'> {feels_like:.0f}&deg; </div>
        <div class='cur-hum'> {humidity}</div>
    </div>
    <div class='cur-icon'><img src='{icon}' /></div>
    <div class='cur-text-info'>
        <div class='cur-desc'> {description} </div>
        <div class='cur-forcast'>{minutely}</div>
    </div>
    <div class='cur-sun'>
        <div class='cur-sunrise cur-sun-entry'>
            <img src='/img/weather/sunrise.png' />
            <div class='cur-sun-text'>{sunrise-time}</div>
        </div>
        <div class='cur-sunset cur-sun-entry'>
            <img src='/img/weather/sunset.png' />
            <div class='cur-sun-text'>{sunset-time}</div>
        </div>

    </div>
    """
    def currently(weather):
        current = weather['current']
        current.update({
            'minutely': minutely(weather['minutely']),
            'description': current['weather'][0]['description'],
            'icon': get_weather_icon(current['weather'][0]['icon']),
            'sunrise-time': _ts2time(current['sunrise']),
            'sunset-time': _ts2time(current['sunset']),
        })
        return CURRENT_TEMPLATE.format(**current)

    def minutely(data):
        prec = list(d['precipitation'] for d in data)
        if all(prec):
            return "no change soon."
        if not any(prec):
            return "no change soon"
        if prec[0]:
            return "clearing up in {} minutes".format([i for i, a in enumerate(prec) if a])[0]
        if prec[0]:
            return "precipitation in {} minutes".format([i for i, a in enumerate(prec) if not a])[0]


    weather_html = WEATHER_TEMPLATE.format(
            sun_info="", 
            currently=currently(weather),
            daily=daily(weather['daily']),
        )

    current_html = currently(weather)
    write_to_www('current-weather', weather, html=current_html, title="Weather")

    WEATHER_HOURLY_TEMPLATE = """
    <div id="w-hourly">
        {hourly}
    </div>
    """
    HOURLY_ENTRY = """
    <div class='hourly-weather-entry'>
        <div class='hwe-icon'><img src='{icon}' /></div>
        <div class='hwe-bar-container'>
            <div class='hwe-filler temp' style="height: {temp_percent}%"></div>
            <div class='hwe-filler precip' style="height: {prob_of_p}%"></div>
        </div>
        <div class='hwe-stat-container'>
            <div class='hwe-stat hwe-temp'>{temp}&deg;</div>
            <div class='hwe-stat hwe-pop'>{prob_of_p}</div>
        </div>
        <div class='hwe-hour'>{hour}h</div>
    </div>
    """
    def hourly(data):
        to_ret = []
        temp_range = [e['feels_like'] for e in data]
        temp_range = (min(temp_range), max(temp_range))
        for entry in data[:24]:
            entry.update({
                "hour": _ts2hour(entry['dt']),
                "icon": get_weather_icon(entry['weather'][0]['icon']),
                "description": get_weather_icon(entry['weather'][0]['description']),
                "temp_percent": 10 + (80 * (entry['feels_like'] - temp_range[0]) / (temp_range[1] - temp_range[0])),
                "prob_of_p": int(entry['pop'] * 100),
                "temp": int(entry['feels_like'])
            })
            to_ret.append(HOURLY_ENTRY.format(**entry))
        return ''.join(to_ret)
    hourly_html = WEATHER_HOURLY_TEMPLATE.format(
        hourly=hourly(weather['hourly']),
    )
    write_to_www('hourly-weather', weather['hourly'], html=hourly_html, title="Hourly Weather")
else:
    write_to_www('hourly-weather', "", title="Weather service is down from ratelimiting :(")


# # Time

# In[48]:




TIMECARD_TEMPLATE = """
<div id='time-curtime'>{time}</div>
<div id='time-cursec'><div id='time-sec-progress' style=''></div> </div>
<div id='time-curdate'>{date}</div>


<script>
function startTime() {{
  var today = new Date();
  var h = today.getHours();
  var m = today.getMinutes();
  var s = today.getSeconds();
  m = checkTime(m);
  ps = (Date.now() / 10 % 6000) / 60;
  document.getElementById('time-curtime').innerHTML = h + ":" + m;
  document.getElementById('time-sec-progress').setAttribute("style", (m%2 ? `width:${{ps}}%; left:0`: `width:${{100-ps}}%; right:0`) + (ps<3?'width:0':''));
  var t = setTimeout(startTime, 500);
}}
function checkTime(i) {{
  if (i < 10) {{i = "0" + i}};
  return i;
}}
startTime();
</script>
"""

data = {
    "time": datetime.datetime.now().strftime("%H:%M"),
    "date": datetime.datetime.now().strftime("%a, %b %d, %Y"),
}
write_to_www("now", data, TIMECARD_TEMPLATE.format(**data), title="Now")


# # location

# In[4]:


# from scrapers import location
# location_data = get_or_reload('location', location._get_locations, 10)
# write_to_www('location', location_data, title="Location")


# # activity tracking

# In[5]:


from scrapers import timeular
from collections import defaultdict
import dateutil
import dateutil.parser


current_activity=get_or_reload('current_activity', timeular.current_activity, 0)
recent_activity=get_or_reload('recent_activity', timeular.recent_activity, 5)


# In[12]:


TRACKER_TEMPLATE = """
<div id='track-current'>
    <div class='tc-title-holder'>
        <div class='tc-color-dot' style="background:{color}77; border-color:{color}"></div>
        <div class='tc-activity-name'>{activity_name}</div>
    </div>
    <div class='tc-info'>
        <div class='tc-activity-note'>{note}</div>
        <div class='tc-activity-time'>{elapsed}</div>
    </div>
</div>
"""

def get_tracking_data(data):
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

def _str2dt(s):
    return datetime.datetime.fromisoformat("{}+00:00".format(s)).astimezone(tz=dateutil.tz.tzlocal())

ACTIVITY_TEMPLATE = """
<div id='activity-tracker-recent'> 
<h1> 1-week activity history </h1>
<div class='atr-calendar'>
    {activity_history_html} 
</div>
</div>
"""

ACTIVITY_BLOCK = """
<div class='atr-block' style='top: {top}%; bottom: {bottom}%; background: {color};'><!-- {comments} -->
</div>
"""

ACTIVITY_DAY = """
<div class='atr-day'>
    {blocks}
</div>
"""

def _toffset(dt):
    return (dt.hour * 60 * 60 + dt.minute * 60 + dt.second) / (24 * 60 * 60)

def _doy(dt):
    return int(dt.strftime("%-j"))

def get_tracking_history(tracker_data):
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
            days[7 - today + _doy(start)].append([0, _toffset(end), te['activity'], te['note'], te['duration']])
    activity_history_html = []
    for day in days:
        blocks = []
        for block in day:
            blocks.append(ACTIVITY_BLOCK.format(top=100*block[0], bottom=100-(100*block[1]), 
                                                color=block[2]['color'], comments=json.dumps(block)))
        activity_history_html.append(ACTIVITY_DAY.format(blocks=''.join(blocks)))
    return {"activity_history_html": ''.join(activity_history_html[-7:])}
tracker_html = TRACKER_TEMPLATE.format(**get_tracking_data(current_activity))
history_html = ACTIVITY_TEMPLATE.format(**get_tracking_history(recent_activity))
write_to_www('activity', data, html=tracker_html, title="Current Activity")
write_to_www('activity-history', data, html=history_html, title="History of Activity")


# In[9]:


recent_activity


# # Calendar

# In[122]:


GoogleScriptEndpoint = "https://script.google.com/macros/s/AKfycbzW8nnI8gkl9TXa_XeUyXDJpxtByLg8IztjUFby1w0Ola56WfY/exec"


# In[124]:


def get_calendar():
    return requests.get(GoogleScriptEndpoint, params={"function": "cal"}).json()
calendar_data = get_or_reload('calendar', get_calendar, 15)

calendar_data.get("events")

AGENDA_TEMPLATE = """
<div id='agenda-container'>
<h2> Today - {today_date} </h2>
{today_events}
<h2> Tomorrow - {tomorrow_date} </h2>
{tomorrow_events}
</div>
"""

AGENDA_EVENT_LIST = """
<div class="a-e-event-list">
    {event_list}
</div>
"""

AGENDA_ENTRY = """
<div class='agenda-entry a-e-status-{age}'>
    <div class="a-e-name a-e-rsvp-{status}"> {name} </div>
    <div class='a-e-dots'></div> 
    <div class="a-e-start"> {start_dt:%H%M} </div>
    <div> - </div> 
    <div class="a-e-end"> {end_dt:%H%M} </div>
</div>
"""

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
def format_event_list(el):
    to_ret = []
    for e in sorted(el, key=lambda e: e['start']):
        print(e)
        ec = {k: v for k, v in e.items()}
        ec['start_dt'] = datetime.datetime.fromtimestamp(ec['start'])
        ec['end_dt'] = datetime.datetime.fromtimestamp(ec['end'])
        ec['age'] = ['DONE', 'STARTED', 'UPCOMING'][(time.time() < ec['start']) + (time.time() < ec['end'])]
        to_ret.append(AGENDA_ENTRY.format(**ec))
    return ''.join(to_ret)

write_to_www('agenda', calendar_data, html=render_agenda(calendar_data), title="Calendar")


# # Weight / fitness / activity

# In[53]:


# SECRETS = json.load(open('secrets.json', 'r'))

# s = requests.session()

# login_page = s.get("https://sso.garmin.com/sso/signin?service=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&webhost=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&source=https%3A%2F%2Fconnect.garmin.com%2Fsignin%2F&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_US&id=gauth-widget&cssUrl=https%3A%2F%2Fconnect.garmin.com%2Fgauth-custom-v1.2-min.css&privacyStatementUrl=https%3A%2F%2Fwww.garmin.com%2Fen-US%2Fprivacy%2Fconnect%2F&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&generateExtraServiceTicket=true&generateTwoExtraServiceTickets=false&generateNoServiceTicket=false&globalOptInShown=true&globalOptInChecked=false&mobile=false&connectLegalTerms=true&showTermsOfUse=false&showPrivacyPolicy=false&showConnectLegalAge=false&locationPromptShown=true&showPassword=true&useCustomHeader=false#")



# t = login_page.text
# csrf_idx = t.index('_csrf" value="') + len('_csrf" value="')
# csrf = t[csrf_idx:csrf_idx+100]



# attempt = s.post(garminURI, {
#     "username": SECRETS['GARMIN']['email'],
#     "password": SECRETS['GARMIN']['pass'],
#     'csrf': csrf,
#     'embed': False
# })


# from IPython.core.display import HTML
# HTML(attempt.text)

print("DONE")
