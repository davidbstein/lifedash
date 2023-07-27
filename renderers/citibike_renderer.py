from .templates import (
    CITIBIKE_TEMPLATE,
    CITIBIKE_STATION,
    )
import json

STATION_SHORT_NAMES = {
    "MacDougal St & Washington Sq": "WSP NW",
    "Sullivan St & Washington Sq": "NYU Law",
    "Washington Pl & 6 Ave": "6th Ave CVS",
    "Carmine St & 6 Ave": "4th St. Metro",
    "Gansevoort St & Hudson St": "Gansevoort",
    "Washington St & Gansevoort St": "River",
    "Hudson St & W 13 St": "Hudson"
}
def render_citibike_status(citibike_data):
    station_list = sorted(citibike_data[:7], key=lambda s: s['lon'])
    station_list_dump = json.dumps(station_list)
    for station in station_list:
        if station['name'] in STATION_SHORT_NAMES:
            station['name'] = STATION_SHORT_NAMES[station['name']]
    station_elements = [
        CITIBIKE_STATION.format(**station)
        for station in station_list
        ]
    station_list_html = ' '.join(station_elements)
    if not citibike_data:
        station_list_html = "no up-to-date citibike data"
    return CITIBIKE_TEMPLATE.format(**locals())
