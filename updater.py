#!/usr/bin/env python
# coding: utf-8
import datetime
import dateutil
import dateutil.parser
import json
import requests
import time
from collections import defaultdict
from threading import Thread

from renderers.render_util import (
    write_to_www,
    update_www,
    )
from renderers import (
    activity_renderer,
    calendar_renderer,
    clock_renderer,
    citibike_renderer,
    fitness_renderer,
    weather_renderer
    )
from scrapers import (
    activity_scraper,
    caching,
    calendar_scraper,
    citibike_scraper,
    weather_scraper,
    garmin_scraper,
    oura_scraper,
    )


SCRIPT_START = time.time()
LAST_CALL = [SCRIPT_START]
def _log_action_completed(event):
    """ simple logging hax """
    since_start = time.time() - SCRIPT_START
    since_last_call = time.time() - LAST_CALL[0]
    LAST_CALL[0] = time.time()
    to_timetriple = lambda elapsed: (elapsed // (60*60), (elapsed // 60) % 60, elapsed % 60)
    format_timerange = lambda elapsed: "{:2.0f}:{:02.0f}:{:02.2f}".format(*to_timetriple(elapsed))
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
    oura_sleep_data = data['oura']['sleep']
    garmin_data = data['wellness']
    calendar_data = data['calendar']
    write_to_www(
        'activity',
        html=activity_renderer.render_tracker_html(activity_data)
    )
    write_to_www(
        'activity-history',
        html=activity_renderer.render_history_html(activity_data, oura_sleep_data, garmin_data, calendar_data)
    )

def update_wellness_tracker(data):
    #['activities', 'sleeps', 'epochs', 'dailies', 'bodyComps', 'userMetrics']
    #write_to_www("readiness", fitness_renderer.render_readiness(data['oura']))
    write_to_www("david-fitness-combined", fitness_renderer.render_fitness_combined(data['wellness'], data['oura'], person_name="david"))
    write_to_www("awake-time", fitness_renderer.render_awake_time(data['oura']))
    write_to_www("fitness", fitness_renderer.render_garmin_data(data['wellness']))

def update_pill_tracker(data):
    calendar_data = data['calendar']
    #write_to_www('pill-timing', html=calendar_renderer.render_pill_timing(calendar_data))
    #write_to_www('pill-history', html=calendar_renderer.render_pill_history(calendar_data))
    write_to_www('pill-combined', html=calendar_renderer.render_pill_combined(calendar_data))

def update_emily_widgets(data):
    print(data['emily.wellness'])
    write_to_www("emily-fitness-combined", fitness_renderer.render_fitness_combined(data['emily.wellness'], data['emily.oura'], person_name="emily"))

def update_citibike(data):
    write_to_www("citibike-status", citibike_renderer.render_citibike_status(data['citibike']))

def final_error_update(data):
    if data['_error_count'] == 0:
        write_to_www("last-update", """
        <div>Last Update</div><div id="last-update-time"> </div>
        <script>(()=>{
        function secsToTime(secs){return `${(h=("00" + Math.floor(secs/3600)).slice(-2)) == "00" ? '': ''+h+"h:"}${(m=("00" + Math.floor(secs/60)).slice(-2)) == "00" ? '': ''+m+"m:"}${(s=("00" + Math.floor(secs%60)).slice(-2)) == "00" ? s: s}s`;}
        function setLastUpdate(){const secs = (Date.now()/1000) - """+str(time.time())+""";document.querySelector("#last-update-time").innerText = `${secsToTime(secs)} ago`;}
        setLastUpdate();
        setInterval(setLastUpdate, 10000);
        })();</script>""")

def get_data():
    print("start data")
    data = {"_error_count": 0}
    data_fn_list = [
        ("activity", activity_scraper.get_activity_data),
        ("calendar", calendar_scraper.get_calendar_data),
        ("citibike", citibike_scraper.get_citibike_data),
#        ("emily.oura", oura_scraper.emily_get_oura_data),
#        ("emily.wellness", garmin_scraper.emily_get_garmin_wellness_data),
        ("oura", oura_scraper.get_oura_data),
        ("weather", weather_scraper.get_weather_data),
        ("wellness", garmin_scraper.get_garmin_wellness_data),
    ]
    for key, fn in data_fn_list:
        try:
            data[key] = fn()
            _log_action_completed(fn.__name__)
        except Exception as e:
            print(f"error in: {fn.__name__}")
            traceback.print_exc()
            data['_error_count'] += 1
    print("end data")
    return data
    
    
def do_update(data):
    print("start update")
    update_fn_list = [
        update_www,
        update_activity_tracker,
        update_calendar,
        update_citibike,
        update_clock,
        #update_emily_widgets,
        update_pill_tracker,
        update_weather,
        update_wellness_tracker,
        final_error_update,
        ]
    def runit(fn):
        try:
            fn(data)
            _log_action_completed(fn.__name__)
        except Exception as e:
            print(f"error in: {fn.__name__}")
            traceback.print_exc()
            data['_error_count'] += 1
    threads = []
    for fn in update_fn_list:
        t = Thread(target=runit, args=(fn,))
        t.start()
        t.join()
        threads.append(t)
    for t in threads:
        t.join()
    print("done update")

if __name__ == "__main__":
    import traceback
    start_ts = time.time()
    print("START SCRIPT")
    data = get_data()
    do_update(data)
    print(f"END SCRIPT. RUNTIME {time.time() - start_ts}")
