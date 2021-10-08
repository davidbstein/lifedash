import datetime
from .templates import (
    WEATHER_TEMPLATE,
    CURRENT_TEMPLATE,
    WEEKLY_FORCAST,
    DAILY_FORCAST,
    WEATHER_HOURLY_TEMPLATE,
    HOURLY_ENTRY,
    )

def _ts2time(ts):
    return "{}:{}".format(datetime.datetime.fromtimestamp(ts).hour, datetime.datetime.fromtimestamp(ts).minute)

def _ts2hour(ts):
    return datetime.datetime.fromtimestamp(ts).hour

def get_weather_icon(icon_str):
    # dont return "http://openweathermap.org/img/wn/{}@2x.png".format(icon_str)
    return "/img/weather/{}.png".format(icon_str)

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

def render_daily_entries(data):
    disp_data = [gen_day_entry(d) for d in data[1:8]]
    return {
        'daily_entries': ''.join(d['html'] for d in disp_data)
    }

def currently(weather):
    current = weather['current']
    current.update({
        'minutely': minutely(weather['minutely']) if 'minutely' in weather else '(forcast down)',
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

def render_current_html(weather_data):
    """ 
    renders the 'current weather' box
    expects a valid response object from the openweathermap APIv2.5 /onecall endpoint
    """
    return currently(weather_data)

def render_hourly_html(weather_data):
    return WEATHER_HOURLY_TEMPLATE.format(
        hourly=hourly(weather_data['hourly']),
    )

def render_weekly_html(weather_data):
    return WEEKLY_FORCAST.format(
        **render_daily_entries(weather_data['daily'])
    )

"""
    current_html = currently(weather)
    hourly_html = WEATHER_HOURLY_TEMPLATE.format(
        hourly=hourly(weather['hourly']),
    )
    weekly_html = WEEKLY_FORCAST.format(**render_daily_entries(weather['daily']))
    weather_html = WEATHER_TEMPLATE.format(
            sun_info="", 
            currently=currently(weather),
            daily=render_daily_entries(weather['daily']),
    )
"""
