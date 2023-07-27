# script to run the raspberry-pi browers. No longer in use.
export DISPLAY:=0
while true
    for pid in (pgrep chromium)
        kill 
    end
    chromium-browser --start-fullscreen
    sleep 3600
end
