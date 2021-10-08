import datetime
from .templates import TIMECARD_TEMPLATE

def render_clock():
   time_data = {
       "time": datetime.datetime.now().strftime("%H:%M"),
       "date": datetime.datetime.now().strftime("%a, %b %d, %Y"),
   }
   return TIMECARD_TEMPLATE.format(**time_data)
