set_color red; /home/pi/.local/share/virtualenvs/lifedash-1xjE3tkN/bin/python3 updater.py 1> /tmp/logcache 2>| ts '[%m-%d %H:%M:%S]'; set_color normal; ts '[%m-%d %H:%M:%S]' < /tmp/logcache
#python updater.py 1> /dev/null 2>| ts '[%Y-%m-%d %H:%M:%S]'
