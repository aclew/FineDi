#!/usr/bin/env python
#
# all the imports
import os
import sqlite3
from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash)

# create app
print __name__
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
# Load default config and override config from an environment variable
app.config.update(dict(
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default'
        ))

all_wavs=['test1.wav', 'test2.wav']
cur_wav= -1
print cur_wav
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/', methods=['GET', 'POST'])
def show_entries():
    #entries = cur.fetchall()
    
    entries=["bel"]
    print cur_wav
    cur_wav += 1
    wav = "audio/" + all_wavs[cur_wav]
    print(request.form.getlist('trs_label'))
    return render_template('show_entries.html', entries=entries, wav=wav)



