#!/bin/bash
#
# This script is useful to launch the app
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR

# Export env variable to specify app path
export PYTHONPATH=$DIR/fineDi:$PYTHONPATH
export FLASK_APP=$DIR/fineDi/diarization_refinement.py

# run app
flask run&
# wait a bit for the app to launch
sleep 1

# open app in firefox
firefox 127.0.0.1:5000&
firefox_pid=`ps | grep firefox | cut -d " " -f 2`
flask_pid=`ps | grep flask | cut -d " " -f 2`

# wait for the firefox window to close and then kill the wsgi server
wait $firefox_pid
kill -15 $flask_pid
