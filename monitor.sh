while true
do
    if ! grep -q "`date '+%Y%m%d %H:%M'`" now.txt
    then
        pid=`ps auxww | grep python | grep whimsy/main.py | awk '{print $2}'`
        if [ ! -z "$pid" ]
        then
            kill -ALRM "$pid"
            kill "$pid" 2>/dev/null
            kill -QUIT "$pid" 2>/dev/null
            kill -9 "$pid" 2>/dev/null
            echo "KILLED! at `date`"
        else
            echo "couldn't find pid to kill!"
        fi
    fi
    sleep $1
done
