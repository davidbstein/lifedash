import json
import datetime

from .templates import (
    HTML_TEMPLATE,
    FIELD_TEMPLATE,
    FIELDBOX_TEMPLATE,
)

def _render(field, raw_data):
    if not raw_data.get('html'):
        assert 'data' in raw_data, f"there is no 'html' or 'data' field available for the {field} block"
        return FIELD_TEMPLATE.format(field=field, data=raw_data['data'], title=raw_data['title'])
    return FIELDBOX_TEMPLATE.format(field=field, html=raw_data['html'])

def write_to_www(field, html="", title=None):
    with open("/home/pi/lifedash/www/raw.json", 'r') as f:
        page_data = json.loads(f.read())
    cur_time = str(datetime.datetime.now())
    page_data.update({
        field: {'html': html, 'ts': 0, "title": title or field},
        "last_update": {"data": cur_time, "title": "Last Update"}
    })
    with open("/home/pi/lifedash/www/raw.json", 'w') as f:
        f.write(json.dumps(page_data))
    update_www()
    
def update_www():
    with open("/home/pi/lifedash/www/raw.json", 'r') as f:
        page_data = json.loads(f.read())
    with open("/home/pi/lifedash/www/index.html", 'w') as f:
        content = ''.join(_render(f, d) for f, d in page_data.items())
        f.write(HTML_TEMPLATE.format(content=content, hour=datetime.datetime.now().hour))
