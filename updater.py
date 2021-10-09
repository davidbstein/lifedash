#!/usr/bin/env python
# coding: utf-8
import datetime
import dateutil
import dateutil.parser
import json
import requests
import time
from collections import defaultdict

from renderers.render_util import (
    write_to_www,
    update_www,
    )
from renderers import (
    activity_renderer,
    calendar_renderer,
    clock_renderer,
    fitness_renderer,
    weather_renderer
    )
from scrapers import (
    activity_scraper,
    caching,
    calendar_scraper,
    weather_scraper,
    garmin_scraper,
    )


SCRIPT_START = time.time()
LAST_CALL = [SCRIPT_START]
def _log_action_completed(event):
    """ simple logging hax """
    since_start = time.time() - SCRIPT_START
    since_last_call = time.time() - LAST_CALL[0]
    LAST_CALL[0] = time.time()
    to_timetriple = lambda elapsed: (elapsed // (60*60), (elapsed // 60) % 60, elapsed % 60)
    format_timerange = lambda elapsed: "{:2.0f}:{:2.0f}:{:2.2f}".format(*to_timetriple(elapsed))
    print(f"{event}\n - {format_timerange(since_start)} ({format_timerange(since_last_call)} total)")


def update_weather(data):
    weather_data = data['weather']
    if weather_data:
        write_to_www('current-weather', html=weather_renderer.render_current_html(weather_data))
        write_to_www('hourly-weather', html=weather_renderer.render_hourly_html(weather_data))
        write_to_www('weekly-weather', html=weather_renderer.render_weekly_html(weather_data))
    else:
        write_to_www('hourly-weather', html="Weather service is down :(")


def update_clock(data):
    write_to_www("now", html=clock_renderer.render_clock())

    
def update_calendar(data):
    calendar_data = data['calendar']
    write_to_www('agenda', html=calendar_renderer.render_agenda(calendar_data))

    
def update_activity_tracker(data):
    activity_data = data['activity']
    sleep_data = data['wellness'].get("sleeps", {})
    write_to_www('activity', html=activity_renderer.render_tracker_html(activity_data))
    write_to_www('activity-history', html=activity_renderer.render_history_html(activity_data, sleep_data))

def update_wellness_tracker(data):
    #['activities', 'sleeps', 'epochs', 'dailies', 'bodyComps', 'userMetrics']
    garmin_data = data['wellness']
    
def update_pill_tracker(data):
    calendar_data = data['calendar']
    write_to_www('pill-timing', html=calendar_renderer.render_pill_timing(calendar_data))
    write_to_www('pill-history', html=calendar_renderer.render_pill_history(calendar_data))

def get_data():
    print("start data")
    data = {}
    data_fn_list = [
        ("activity", activity_scraper.get_activity_data),
        ("weather", weather_scraper.get_weather_data),
        ("calendar", calendar_scraper.get_calendar_data),
        ("wellness", garmin_scraper.get_garmin_wellness_data),
    ]
    for key, fn in data_fn_list:
        try:
            data[key] = fn()
            _log_action_completed(fn.__name__)
        except Exception as e:
            print(f"error in: {fn.__name__}")
            traceback.print_exc()
    print("end data")
    return data
    
    
def do_update(data):
    print("start update")
    update_fn_list = [
        update_www,
        update_weather,
        update_clock,
        update_calendar,
        update_activity_tracker,
        update_wellness_tracker,
        update_pill_tracker,
        ]
    for fn in update_fn_list:
        try:
            fn(data)
            _log_action_completed(fn.__name__)
        except Exception as e:
            print(f"error in: {fn.__name__}")
            traceback.print_exc()
    print("done update")

if __name__ == "__main__":
    import traceback
    print("START SCRIPT")
    data = get_data()
    do_update(data)
    print("END SCRIPT")