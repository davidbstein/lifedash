HTML_TEMPLATE = """
<html>
<head>
<link rel="stylesheet" href="/css/chrome.css" type="text/css" />
<script>
window.START = new Date();
setInterval(function(){{
  if (((new Date() - window.START)/1000) > 120) location.reload();
}}, 10000)
</script>
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


##################################
## ACTIVITY TRACKING (TIMEULAR) ##
##################################

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

PILL_TIMING_TEMPLATE = """
<div id='pill-timing-container'>
  {current_pill}
  {timing_history}
</div>
"""

PILL_TIMING_CURRENT = """
<div class='p-t-current'>
  <div class='p-t-start'> 
    Pill Started: {current_pill_time:%H:%M} 
  </div>
  <div class='p-t-age'> 
    Total: {current_pill_age} 
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
<div class='p-t-h-day'>
  {taken_day}
</div>
<div class='p-t-h-hour'>
  {taken_hour}
</div>
</li>
"""

#############
## FITNESS ##
#############

FITNESS_BAR_TEMPLATE = """
<div id='fitness-bar-container'>
    THIS IS WHERE THE FITNESS BAR GOES
</div>
"""
