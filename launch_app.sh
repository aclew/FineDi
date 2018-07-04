#!/bin/bash
#
# This script is useful to launch the app
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR


# Export env variable to specify app path
export FLASK_CONFIG=$DIR/config.py
export PYTHONPATH=$DIR/fineDi:$PYTHONPATH
export FLASK_APP=$DIR/fineDi/diarization_refinement.py

# Check if finedi/static/audio and finedi/static/media exist. If not, create them
if [ ! -d $DIR/fineDi/static/audio ]; then
    echo "creating audio dir"
    mkdir $DIR/fineDi/static/audio 
fi
if [ ! -d $DIR/fineDi/static/media ]; then
    echo "creating media dir"
    mkdir $DIR/fineDi/static/media
fi

# run app
flask run&
# wait a bit for the app to launch
sleep 2

# get flask pid
flask_pid=`ps | grep flask | awk '{print $1}'`

# open app in firefox
firefox 127.0.0.1:5000&
# wait again for firefox to launch
sleep 5

# get firefox pid
firefox_pid=`ps | grep firefox | awk '{print $1}'`

# wait for the firefox window to close and then kill the server that runs flask
wait $firefox_pid
kill -15 $flask_pid
