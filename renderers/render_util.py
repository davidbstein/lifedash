import json
import datetime
import os

from .templates import (
    HTML_TEMPLATE,
    FIELD_TEMPLATE,
    FIELDBOX_TEMPLATE,
)

DATA_JSON_PATH = "/home/pi/lifedash/www/raw.json"

def _render(field, raw_data):
    if not type(raw_data) == dict or not raw_data.get('html'):
        return f"<!--- {field} was not a dict with an `html` field set --->"
    return FIELDBOX_TEMPLATE.format(field=field, html=raw_data['html'])

def write_to_www(field, html="", title=None):
    if not os.path.exists(DATA_JSON_PATH):
        with open(DATA_JSON_PATH, 'w') as f:
            f.write("{}")
    with open(DATA_JSON_PATH, 'r') as f:
        try:
            page_data = json.loads(f.read())
        except json.decoder.JSONDecodeError as e:
            import traceback
            traceback.print_exc()
            print("render_til(write_to_www): JSON error")
            os.remove(DATA_JSON_PATH)
            update_www({"ERROR": {"html": str(e)}})
            return 
    cur_time = str(datetime.datetime.now())
    page_data.update({
        field: {'html': html, 'ts': 0, "title": title or field},
    })
    with open("/home/pi/lifedash/www/raw.json", 'w') as f:
        f.write(json.dumps(page_data))
    update_www()
    
def update_www(data=None):
    if not data:
        with open(DATA_JSON_PATH, 'r') as f:
            page_data = json.loads(f.read())
    else:
        page_data = data
    last_css_update = os.path.getmtime("/home/pi/lifedash/www/css/chrome.css")
    with open("/home/pi/lifedash/www/index.html", 'w') as f:
        content = ''.join(_render(f, d) for f, d in page_data.items())
        f.write(HTML_TEMPLATE.format(content=content, hour=datetime.datetime.now().hour, last_css_update=last_css_update))
