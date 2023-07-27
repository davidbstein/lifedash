import math
import json
import datetime
import time
from collections import defaultdict

from renderers.templates import (
    AWAKE_TIME_CONTAINER,
    FITNESS_ACTIVITY_ENTRY,
    FITNESS_BAR_TEMPLATE,
    FITNESS_COMBINED,
    FITNESS_DAY_ENTRY,
    FITNESS_WEEK_ENTRY,
    FITNESS_WORKOUT_ENTRY,
    READINESS_CONTAINER,
)



HISTORY_LEN = 7*3 - 1
DEFAULT_HEARTRATE = 155
WORKOUT_HEARTRATE = 200
# effort levels go from 0 to 4;

def format_workout_daily_detail(workout_type, entries):
    total_heartbeats = sum([
        entry.get('averageHeartRateInBeatsPerMinute', DEFAULT_HEARTRATE) * entry.get('durationInSeconds', 0) / 60
        for entry in entries
    ], 0)
    effort_thresholds = [minutes * WORKOUT_HEARTRATE for minutes in [2, 45, 75, 120, 240]]
    type_specific_effort = len([1 for threshold in effort_thresholds if total_heartbeats > threshold])
    if workout_type == "RUNNING":
        km_thresholds = [0, 7, 12, 17, 22]
        total_distance = sum([entry['distanceInMeters'] for entry in entries], 0)
        type_specific_effort = len([
            1 for threshold in km_thresholds if total_distance / 1000 > threshold
        ])
    if workout_type == "WALKING":
        low_km_thresholds = [0, 10, 20, 35, 50]
        high_km_thresholds = [0, 5, 10, 15, 20]
        km_thresholds = low_km_thresholds
        total_distance = sum([entry['distanceInMeters'] for entry in entries], 0)
        type_specific_effort = len([
            1 for threshold in km_thresholds if total_distance / 1000 > threshold
        ])
    if workout_type == "STRENGTH_TRAINING":
        minute_thresholds = [1, 15, 30, 60, 120]
        total_time = sum([entry['durationInSeconds'] / 60 for entry in entries], 0)
        type_specific_effort = sum((total_time > threshold for threshold in minute_thresholds), 0)
    if workout_type == "INDOOR_CYCLING":
        minute_thresholds = [15, 30, 60, 90, 120]
        type_specific_effort = sum((
            total_heartbeats / WORKOUT_HEARTRATE > threshold
            for threshold in minute_thresholds
        ), 0)
    if workout_type == "INDOOR_ROWING":
        minute_thresholds = [5, 15, 30, 60, 90]
        type_specific_effort = sum((
            total_heartbeats / WORKOUT_HEARTRATE > threshold
            for threshold in minute_thresholds
        ), 0)
    summary = [
        {
            '_MINUTES': entry.get("durationInSeconds", -1) / 60,
            '_MILES'  : entry.get("distanceInMeters", -1) / 1609.34,
            '_BEATS'  : total_heartbeats,
            '_EFFORT' : type_specific_effort,
        }
        for entry in entries
    ]
    return FITNESS_WORKOUT_ENTRY.format(**locals())


def format_fitness_day(days_ago, workout_list, activity_level, rest_count):
    # duration
    minutes_thresholds = [1, 30, 45, 60, 90]
    duration = sum(
        [workout['durationInSeconds'] for workout in workout_list],
        0)
    quantized_duration = len([1 for threshold in minutes_thresholds if threshold < duration*60])

    # effort
    heartbeats = sum(
        [workout['durationInSeconds'] * workout.get('averageHeartRateInBeatsPerMinute', 150) / 60
         for workout in workout_list],
        0)
    _workout_heartrate = WORKOUT_HEARTRATE
    beats_thresholds = [_workout_heartrate * threshold for threshold in minutes_thresholds]
    quantized_heartbeats = len([1 for threshold in beats_thresholds if threshold < heartbeats])

    # type-specific workout info
    activities = defaultdict(list)
    for workout in workout_list:
        activities[workout['activityType']].append(workout)
    workout_entries = ''.join([
        format_workout_daily_detail(workout_type, entries)
        for workout_type, entries in activities.items()
    ])
    activity_entry = format_daily_activity_level_entry(activity_level)
    rest_count = rest_count
    return FITNESS_DAY_ENTRY.format(**locals())

def format_daily_activity_level_entry(activity_level):
    if not activity_level:
        return ''
    score = 10 * math.log(max(1, activity_level['daily_movement']))
    # score = ['score']
    return FITNESS_ACTIVITY_ENTRY.format(**locals())

def render_fitness_combined(garmin_data, oura_data, person_name="david"):
    return FITNESS_COMBINED.format(**{
        "person": person_name,
        "fitness_bar": render_fitness_bar(garmin_data, oura_data),
        "readiness_container": render_readiness(oura_data), 
    })

def render_fitness_bar(garmin_data, oura_data):
    # note: for reasons, I build everything backwards and then reverse it.
    #['activities', 'sleeps', 'epochs', 'dailies', 'bodyComps', 'userMetrics']
    #print(json.dumps(garmin_data, indent="  "))
    oura_activities = oura_data['activity']
    activity_level_history = [{} for _ in range(HISTORY_LEN)]
    workouts = garmin_data['activities']
    workout_history = [[] for _ in range(HISTORY_LEN)]
    today = datetime.date.today()
    for workout in workouts:
        dt = datetime.datetime.fromtimestamp(workout['startTimeInSeconds'])
        days_ago = (today-dt.date()).days
        if days_ago >= HISTORY_LEN:
            continue
        workout_history[days_ago].append(workout)
    rest_counts = []
    cur_rest_count = 0
    for days_ago, workouts in reversed(list(enumerate(workout_history))):
        #print(f"days ago: {days_ago} workouts: {len(workouts)} cur_rest: {cur_rest_count}")
        cur_rest_count += 1
        if len(workouts):
            cur_rest_count = 0
        rest_counts.append(cur_rest_count)
    rest_counts = reversed(rest_counts)
    for activity in oura_activities:
        day = datetime.date.fromisoformat(activity['summary_date'])
        days_ago = (today-day).days
        if days_ago >= HISTORY_LEN:
            continue
        activity_level_history[days_ago] = activity
    fitness_day_htmls = [
        format_fitness_day(days_ago, workout_list, activity_level, rest_count)
        for days_ago, (workout_list, activity_level, rest_count)
        in enumerate(reversed(list(zip(workout_history, activity_level_history, rest_counts))))
    ]
    fitness_weeks = []
    for idx in range(0, len(fitness_day_htmls), 7):
        entries = fitness_day_htmls[idx:idx+7]
        daily_entries=''.join(entries)
        fitness_weeks += FITNESS_WEEK_ENTRY.format(
            daily_entries=daily_entries,
            num_days=len(entries),
            history_len=HISTORY_LEN,
        )
    return FITNESS_BAR_TEMPLATE.format(**{
        "fitness_history": ''.join(fitness_weeks),
        "history_len": HISTORY_LEN,
    })

def render_readiness(oura_data):
    oura_readiness = oura_data['readiness'][-1]
    oura_activity = oura_data['activity'][-1]
    oura_sleep = oura_data['sleep'][-1]
    readiness_score = oura_readiness['score']
    rest_mode = "" # manually set in oura app... ["", "entering rest", "rest", "entering recovery", "recovery"][oura_readiness.get('rest_mode_state',0)]
    if rest_mode:
        rest_mode = f"({rest_mode})"
    recovery_index = oura_readiness['score_recovery_index']
    resting_hr = oura_sleep['hr_lowest']
    return READINESS_CONTAINER.format(**locals())


def render_awake_time(oura_data):
    oura_sleep = oura_data['sleep'][-1]
    oura_heartrate = oura_data['heartrate']
    last_oura_sync = int(datetime.datetime.timestamp(
        datetime.datetime.fromisoformat(oura_heartrate[-1]['timestamp'])
    ))
    last_wakeup_ts = oura_sleep['bedtime_end']
    sync_threshold_hours = 20
    return AWAKE_TIME_CONTAINER.format(**locals())

def render_garmin_data(garmin_data):
    import json
    weight = ([{"weightInGrams": 0}] + garmin_data['bodyComps'])[-1]["weightInGrams"] / 453.592
    if weight == 0:
        weight = ""
    return f"""
    {int(weight)} lbs
    <!-- {json.dumps(garmin_data, indent=2)} -->
"""
