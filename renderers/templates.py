HTML_TEMPLATE = """
<html>
<head>
<link rel="stylesheet" href="/css/chrome.css?{last_css_update}" type="text/css" />
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="icon" href="data:,">
<script>
window.START = new Date();

if (window.self !== window.top)
    setInterval(function(){{
        if (((new Date() - window.START)/1000) > 120) location.reload();
    }}, 10000);
</script>
</head>
<body class="hour-{hour}" style="background-image: url('/img/bgs/hours/bg{hour}.jpg')">
<div class="container">
{content}
</pre>
</div>
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

#############
## WEATHER ##
#############

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

###########
## CLOCK ##
###########


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
    document.getElementById('time-sec-progress')
        .setAttribute("style", (m%2 ? `width:${{ps}}%; left:0`: `width:${{100-ps}}%; right:0`) + (ps<3?'width:0':''));
    var t = setTimeout(startTime, 500);
  }}
  function checkTime(i) {{
    if (i < 10) {{i = "0" + i}};
    return i;
  }}
  startTime();
</script>
"""

#####################
## CITIBIKE STATUS ##
#####################

CITIBIKE_TEMPLATE = """
<div id='citibike-status-container'>
{station_list_html}
<!--- {station_list_dump} --->
</div>
"""

CITIBIKE_STATION = """
<div class='cb-s-station cb-s-station-status-{station_status}'>
  <div class='cb-s-s-name'>
    {name}
  </div>
  <div class='cb-s-s-infobar'>
    <div class='cb-s-s-capacity'>
      {capacity}
    </div>
    <div class='cb-s-s-num_bikes_available'>
      <div class='cb-s-s-bike-count'>
        {num_bikes_available}
      </div><div class='cb-s-s-ebike-count'>
        {num_ebikes_available}
      </div>
    </div>
    <div class='cb-s-s-num_docks_available'>
      {num_docks_available}
    </div>
  </div>
</div>
"""

##################################
## ACTIVITY TRACKING (TIMEULAR) ##
##################################

TRACKER_TEMPLATE = """
<div id='track-current'>
    <div class='tc-title-holder'>
        <div class='tc-color-dot' style="background:{color}77; --tracker-color:{color}; border-color:var(--tracker-color);"></div>
        <div class='tc-activity-name'>{activity_name}</div>
    </div>
    <div class='tc-info'>
        <div class='tc-activity-note'>{note}</div>
        <div class='tc-activity-time'>{elapsed}</div>
    </div>
</div>
"""
TRACKER_TIMEULAR_TAG = """
<span class="tc-timeular-tag" style="background: {bgcolor}77;">#{label}</span>
"""
ACTIVITY_TEMPLATE = """
<div id='activity-tracker-recent'> 
    <h1> 1-week activity history </h1>
    <div class='atr-calendar'>
      <div class='atr-cal-line' style="top:0%" ></div>
      <div class='atr-cal-line' style="top:25%" ></div>
      <div class='atr-cal-line' style="top:50%" ></div>
      <div class='atr-cal-line' style="top:75%" ></div>
      <div class='atr-cal-line' style="top:100%" ></div>
        {activity_history_html} 
    </div>
</div>
"""

ACTIVITY_BLOCK = """
<div class='atr-block atr-id-{atr_id}' style='top: {top}%; bottom: {bottom}%; background: {color};'>
<!-- {comments} -->
</div>
"""

ACTIVITY_DAY = """
<div class='atr-day'>
    {blocks}
</div>
"""


##############
## CALENDAR ##
##############

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
    <div class="a-e-start"> {start_dt:%H:%M} </div>
    <div> - </div> 
    <div class="a-e-end"> {end_dt:%H%M} </div>
</div>
"""

PILL_COMBINED_TEMPLATE = """
<div id="pill-combined-container">
   <div class='p-c-section'>
     <div id='pill-timing-container'>
       {current_pill}
     </div>
   </div> <div class='p-c-section'>
      <div id='pill-history-container'>
       {timing_history}
     </div>
   </div>
</div>
"""

PILL_TIMING_TEMPLATE = """
<div id='pill-timing-container'>
  {current_pill}
</div>
"""

PILL_HISTORY_TEMPLATE = """
<div id='pill-history-container'>
  {timing_history}
</div>
"""

PILL_TIMING_CURRENT = """
<div class='p-t-current'>
  <div class='p-t-current-size-{current_pill_size}'></div>
  <div class='p-t-start'>
    <div class='p-t-time'>
        {current_pill_time:%H:%M} 
    </div>
    <div class='p-t-label'>
        Pill Taken
    </div>
  </div>
  <div class='p-t-age'> 
    <div class='p-t-elapsed'>
        {current_pill_age} 
    </div>
    <div class='p-t-agebar'>
        <div class='p-t-agebar-filler' style="right:calc(100% * {current_pill_remaining})"></div>
    </div>
    <div class='p-t-label'>
        Elapsed Pill
    </div>
  </div>
</div>
"""

PILL_TIMING_NO_CURRENT = """
<div class='p-t-not-now'> 
  No currently tracked pill
</div>
"""

PILL_TIMING_HISTORY = """
<div class='p-t-history'> 
  <div id='p-t-hist-label'>History:</div>
  <ul>
    {pill_history}
  </ul>
</div>
"""

PILL_TIMING_HISTORY_ENTRY = """
<li class='p-t-h-{taken} p-t-h-entry'>
  <div class='p-t-d-size p-t-d-size-{taken_size}'></div>
  <div class='p-t-d-info-container'>
    <div class='p-t-h-day'>
      {taken_day}
    </div>
    <div class='p-t-h-hour'>
      {taken_hour}
    </div>
  </div>
</li>
"""

#############
## FITNESS ##
#############
FITNESS_COMBINED = """
    <div class='f-c-title'>
        {person}
    </div>
    <div class='f-c-readiness'>
        {readiness_container}
    </div>
    <div class='f-c-fitness-bar'>
        {fitness_bar}
    </div>
"""

FITNESS_BAR_TEMPLATE = """
<div class='fitness-bar-container'>
    <div class='f-b-history' style='--day-width: calc(100% / {history_len});'>
        {fitness_history}
    </div>
</div>
"""

FITNESS_DAY_ENTRY = """
<div class='f-b-daily-entry f-b-daily-rest-{rest_count}'>
    <div class='f-b-effort-level f-b-effort-level-{quantized_heartbeats}'> </div>
    {workout_entries}
    {activity_entry}
</div>
"""

# style="width: calc( ({num_days} * 100% / {history_len}) - .5em )">
FITNESS_WEEK_ENTRY = """
<div class='f-b-week-entry'>
    {daily_entries}
</div>
"""

FITNESS_WORKOUT_ENTRY = """
<div class='f-b-workout f-b-workout-{workout_type} f-b-effort-level-{type_specific_effort}'> 
    <!--- {summary} --->
</div>
"""

FITNESS_ACTIVITY_ENTRY = """
    <div class='f-b-activity-level' style="top: calc(120% - {score}%);"> </div>
"""


READINESS_CONTAINER = """
<div class='readiness-container'>
  <div class='r-c-stat r-c-readiness'>
    <div class='r-c-key'>Readiness</div>
    <div class='r-c-val'>{readiness_score}</div>
  </div> <div class='r-c-stat r-c-recovery_index'>
    <div class='r-c-key'>Recovery Index</div>
    <div class='r-c-val'>{recovery_index} {rest_mode}</div>
  </div> <div class='r-c-stat r-c-rhr'>
    <div class='r-c-key'>Resting HR</div>
    <div class='r-c-val'>{resting_hr}</div>
  </div>
</div>
"""

AWAKE_TIME_CONTAINER = """
<div id='awake-time-container'>
  <div id='awake-time-render-target'></div>
  <div id='awake-time-label'>total time awake</div>
  <script>
(function(){{
    const updater = function(){{
        const last_sync_ts = {last_oura_sync} * 1000;
        const wakeup_ts = {last_wakeup_ts} * 1000;
        const awake_secs = (new Date() - new Date(wakeup_ts)) / 1000;
        const sync_secs = (new Date() - new Date(last_sync_ts)) / 1000;
        const is_synced = sync_secs < (60*60*{sync_threshold_hours});
        let ts = awake_secs;
        let hrs = Math.floor(ts/3600) % 60;
        let mins = Math.floor(ts/60) % 60;
        let ts_formatted = `${{hrs}}h ${{mins}}m`;
        if (is_synced) {{
            document.getElementById('awake-time-render-target').innerHTML = ts_formatted;
        }} else {{
            document.getElementById('awake-time-render-target').innerHTML = "";
        }}
        ts = sync_secs;
        hrs = Math.floor(ts/3600) % 60;
        mins = Math.floor(ts/60) % 60;
        ts_formatted = `${{hrs}}h ${{mins}}m`;
        document.getElementById('awake-time-label').innerHTML = `${{ts_formatted}} since last sync`;       
    }};
    updater();
    setInterval(updater, 10000);
}})();
  </script>
</div>
"""
