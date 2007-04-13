while true
do
    if ! grep -q "`date '+%Y%m%d %H:%M'`" now.txt
    then
        pid=`ps auxww | grep python | fgrep main.py | awk '{print $2}'`
        if [ ! -z "$pid" ] # else it's just not running
        then
            kill "$pid" 2>/dev/null
            sleep 0.1
            kill -QUIT "$pid" 2>/dev/null
            sleep 0.1
            kill -9 "$pid" 2>/dev/null

            echo "KILLED! at `date`"

            sleep 1
            tail -n100 out.txt | grep -A20 ^Traceback

        fi
    fi
    sleep $1
done
