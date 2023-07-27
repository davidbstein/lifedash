import requests
import time
from .caching import get_or_reload
from scrapers.secrets import (
  SECRETS,
  SETTINGS,
)

CITIBIKE_STATION_INFO_ENDPOINT = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
CITIBIKE_STATION_STATUS_ENDPOINT = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
LOCATIONS = SETTINGS['LOCATIONS']
"""
INFO
{"data":
 {"stations":[
     {"external_id":"66db237e-0aca-11e7-82f6-3863bb44ef7c",
      "has_kiosk":true,
      "rental_methods":["CREDITCARD","KEY"],
      "legacy_id":"72",
      "eightd_has_key_dispenser":false,
      "region_id":"71",
      "name":"W 52 St & 11 Ave",
      "short_name":"6926.01",
      "lon":-73.99392888,
      "station_type":"classic",
      "lat":40.76727216,
      "capacity":52,
      "eightd_station_services":[],
      "station_id":"72",
      "rental_uris": ...
      "electric_bike_surcharge_waiver":false}...

STATUS
{data: {stations: [
  "num_bikes_available": 0,
  "legacy_id": "72",
  "num_bikes_disabled": 0,
  "is_installed": 0,
  "station_id": "72",
  "station_status": "out_of_service",
  "last_reported": 1656077952,
  "is_returning": 0,
  "num_docks_available": 52,
  "num_docks_disabled": 0,
  "eightd_has_available_keys": false,
  "num_ebikes_available": 0,
  "is_renting": 0
"""



def _load_citibike_data():
    resp = requests.get(CITIBIKE_STATION_INFO_ENDPOINT)
    stations = sorted(
        resp.json()['data']['stations'],
        key=lambda station: min([(2*(lat-station['lat']))**2+(lon-station['lon'])**2 for lat, lon in LOCATIONS.values()])
    )
    resp = requests.get(CITIBIKE_STATION_STATUS_ENDPOINT)
    station_status_map = {station['station_id']: station for station in resp.json()['data']['stations']}
    for station in stations:
        station.update(station_status_map[station['station_id']])
    return {
        "last_update_ts": time.time(),
        "stations": stations,
    }

def get_citibike_data():
    to_ret = get_or_reload('citibike', _load_citibike_data, 1)
    if time.time() - to_ret.get("last_update_ts", 0) < 2*60*1000:
        return to_ret['stations']
    return []
