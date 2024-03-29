import requests

from .caching import get_or_reload

# Note: this meat of this function is in the google script
CALENDAR_ENDPOINT = "https://script.google.com/macros/s/AKfycbzW8nnI8gkl9TXa_XeUyXDJpxtByLg8IztjUFby1w0Ola56WfY/exec"
CALENDAR_ENDPOINT = "https://script.google.com/macros/s/AKfycbyOLO9otOCsHgn8SDmmUkwiF1Z-I4dy_aI0kCV1KRF5lth8S5qEyQvNZlpUdYLQpQ24/exec"

def _get_calendar_data():
    return requests.get(CALENDAR_ENDPOINT, params={"function": "cal"}).json()

def get_calendar_data():
    return get_or_reload('calendar', _get_calendar_data, 15)
