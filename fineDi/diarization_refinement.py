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

#all_wavs=['test1.wav', 'test2.wav']
#cur_wav= -1
#print cur_wav
#app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.route('/')
def index():
    """ TODO DEFINE
        Let the user choose what routine (s)he wants to use
        to refine the diarization. 
        Suggested routines: - treat all wavs
                                - which transcription to use ? gold ? Diartk ?
                            - treat one wav
                                - give name
                                - which transcription to use ? gold ? Diartk ?
                            - upload one wav + transcription
    """
    return "hello world"

@app.route('/all_wavs/<wav_name>', methods=['GET', 'POST'])
def treat_all_wavs(wav_name='test1.wav'):
    """ This function creates the app
        when the user is treating all the wavs. 
        It gets the current wav but also the previous and the next.
        This page can be accessed in the browser by going directly 
        to localhost/all_wavs/<wav_name> , where wav_name is
        the name of the wav you want to treat. 

        TODO: add what kind of transcription you want to treat.
    """
    #entries = cur.fetchall()
    wav_list = get_wav_list()
    
    # try to get the position of current wav in list
    try:
        wav_index = wav_list.index(wav_name)
        print wav_list
        print wav_index
        # get previous wav
        if wav_index > 0:
            prev_wav = wav_list[wav_index - 1]
        else:
            prev_wav = None
        
        # get next wav
        if wav_index < len(wav_list) - 1:
            next_wav = wav_list[wav_index + 1]
        else:
            next_wav = None
    except:
        # if the current wav is not in list, throw error page
        pass # TODO create error page

    # labels that can be put to the segment
    entries=[" laugh", " cry", " speech", " do not change annotation"]
    
    #wav = "audio/" + wav_name
    #wav = os.path.join(app.instance_path, 'static', 'audio', wav_name)
    print(request.form.getlist('trs_label'))
    return render_template('show_entries.html', entries=entries, wav=wav_name,
                           next_wav=next_wav, prev_wav=prev_wav)


def get_wav_list():
    """ Get all the wav files in the static folder
        and return them as a list.
        Useful when routine used is to treat all the wavs.
    """
    print app.root_path
    return os.listdir(os.path.join(app.root_path, 'static', 'audio'))
