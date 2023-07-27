#!/bin/sh
# old script from when I used cron instead of system
cd /home/pi/lifedash/
/usr/bin/flock -w0 /tmp/dashboard.lock /usr/bin/fish update_command.fish
