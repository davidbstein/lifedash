# lifedash
A physical dashboard for everyday life. Requires a chron to run at some regular interval to update some data, but is otherwise completely static. Meant to run on a raspberry pi or equivalently cheap micromachine.

## setup

create a file called `secrets.json`. Make sure it has all the expected fields.
create a file called `settings.json`. Make sure it has all the expected fields.
set up the crontab.


## Adding a new data source

NOTE: scrapers will get called every minute. Use a cache to avoid getting rate limited.

 1. create a scraper function that returns a dict of data.
    - usually located in `scrapers/<service>_scraper.py`
    - usually has a function `get_<service>_data()`
 2. register the scraper in `updater.py`
    - add your function and a key to the`data_fn_list` variable in `get_data`



## Adding a new widget

1. Make sure the data you need is already in the updater, following the instructions above
 2. create a function that returns raw HTML
    - usually:
      - add some templates to `templates.py`
      - create a file `<widget_name>_renderer.py` in the `renderers/` folder.
 3. if needed register a new update function with `updater.py`
    - create a new function `update_<widget_name>(data)`
       - this function will be called automatically every minute,
       - `data` is a dictionary. Keys are the labels in `get_data`. Values are the most recent non-error responses from the scrapers.
    - each update function is isolated. If one breaks, the rest will keep running.
 4. have the updater call your new renderer.
    - Any HTML passed to the `write_to_www` function will appear on the dashabord.


## Setup on Raspberry Pi

  1. Check out repo into home directory
  1. Set up `secrets.json` and `settings.json`
  1. Check data sources in the `do_update` function in `updater.py`
  1. set up browser kiosk for autostart: `cp system_scripts/lib_systemd_system_kiosk /lib/systemd/system/kiosk`
  1. set up server run script: `cp system_scripts/lib_systemd_system_webserver /lib/systemd/system/webserver`
  1. install kiosk dependancies: `apt install xdotool upstart`
  1. set services to autostart: `sudo systemctl enable kiosk; sudo systemctl enable webserver`
  1. Start the servers `sudo service kiosk restart; sudo service webserver restart`

for logs, use `journalctl`. E.g.,  `grc journalctl -f -n100`
