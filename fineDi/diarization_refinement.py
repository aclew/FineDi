#!/usr/bin/env python
#
# all the imports

"""
FineDi is an app, based on Flask (a web app developpement toolkit for python)
created to refine manually the results of a labelisation.

The current script creates the app (locally) and implements the different pages
that are accessible by the user, as well as the functionnalities associated 
with these pages.

To link a url to a python function with flask, simply add the decorator:
    @app.route('your/url')

and to tell the python function to display a page: 
    return render_template('template.html')

The implemented pages here are: 
    - index: the user can select between different routines
    - treat_all_wavs: the user can manipulate the label of the wav file
    - success: page displayed when all the segments have been treated
    - error: page displayed when an error is encountered
    - create_segments: gather the segments that will be labelled
    - pick_up: allow the user to restart where they stopped at the previous 
      session
"""

# imports
import os
import sqlite3
from flask import (Flask, request, session, g, redirect, url_for, abort,
                   render_template, flash)
import ipdb
from collections import defaultdict
import subprocess
from tempfile import mkstemp
from os import remove
from shutil import move

from utils import *
# import global variables
from task import *

# create app
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py
# Load default config and override config from an environment variable
app.config.update(dict(
        SECRET_KEY='development key',
        USERNAME='admin',
        PASSWORD='default',
        MEDIA_ROOT='static/media'
        ))

# accessible urls
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
    wav_list = get_wav_list(os.path.join(app.root_path, 'static', 'audio'))


    ## labels for tasks
    #talker_lab =  ['CHI', 'OCH', 'FA', 'MA']
    #vocal_mat_lab = ['cry', 'laugh', 'non-canonical babbling',
    #                 'canonical babbling', 'undecided', 'wrong']

    # define global variables
    #flask.g.task2col = {'talker labels': 7, 'vocal maturity': 6}
    #flask.g.task2choices = {'talker labels': talker_lab,
    #                        'vocal maturity': vocal_mat_lab}

    return render_template('index.html')

@app.route('/choice', methods=['POST', 'GET'])
def task_choice():
    """ Ask the user if they want to change the labels for the 'CHI' speaker,
        or if they want to check the speaker labels
    """
    if request.method == 'POST':
        print "postpostpostpostpostpostpostpo"
        task = request.form.getlist('task')[0]
        print task
        print type(task)
        write_task(task)
        return redirect(url_for('create_segments'))


    return render_template('choose_column.html')

@app.route('/continue')
def pick_up():
    """ If the user chose to continue, we look at the .lock files
    to check which files were already treated
    """
    wav_list = get_wav_list(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))

    locks = os.listdir(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))
    # remove first dot and .lock, to match names with wav
    locks = [fin[1:-5] for fin in locks if fin.endswith('lock')]

    # check matching files in both lists
    untreated = [wav for wav in wav_list if not wav in locks]

    first_wav = untreated[0]

    return redirect(url_for('treat_all_wavs', wav_name=first_wav))

@app.route('/creating')
def create_segments():
    """ Take each wav, retrieve all the annotated segments,
        cut the wav into the segments corresponding to 'CHI'
        and check the labels.
        The names of the outputed wavs are :
            in_wav_on_off_spkr_lab.wav
        where in_wav is the input wav that is segmented, on is
        the time when the segment starts, off the time when the
        segment ends, spkr is the name of the speaker and label
        is the annotation associated with this speaker

    """
    # start by removing all the wavs in the media folder
    # first get all the wavs
    wav_list = get_wav_list(os.path.join(app.root_path, 'static', 'audio'))

    # for each wav, retrieve the labels
    for wav_name in wav_list[0:1]:
        wav_rttm_dict = read_rttm(wav_name)
        for on, dur, lab in wav_rttm_dict['CHI']:
            wav_path = os.path.join(app.root_path, 'static',
                                    'audio', wav_name)
            # skip empty segments
            if dur <= 0:
                continue
            # define output wav path
            output_wav = wav_name.split('.')[0] + '_{}_{}_{}.wav'.format(on,
                                                                         dur,
                                                                         lab)
            output_path = os.path.join(app.root_path,
                                       app.config['MEDIA_ROOT'],
                                       output_wav)

            # create output wave name
            cmd=['sox', wav_path, output_path, 'trim', str(on), str(dur)]
            subprocess.call(cmd)

    # return first wav of the list to start manual annotation
    temp_wav_list = get_wav_list(os.path.join(app.root_path,
                                 app.config['MEDIA_ROOT']))

    first_wav = temp_wav_list[0]
    return redirect(url_for('treat_all_wavs', wav_name=first_wav))



@app.route('/all_wavs/<wav_name>', methods=['GET', 'POST'])
def treat_all_wavs(wav_name='test1.wav'):
    """ This function displays a interactive page, where the user
        can listen to the segment and choose some labels. 
        It gets the current wav but also the previous and the next.
        This page can be accessed in the browser by going directly 
        to localhost/all_wavs/<wav_name> , where wav_name is
        the name of the wav you want to treat. 
        When the form with the labels is submitted, this function 
        changes the corresponding line in the RTTM and redirects the 
        user to the next segment.

        TODO: add what kind of transcription you want to treat.
    """
    #task = flask.g.get('task')
    task = read_task()

    for key in task2choices:
    # if no wav is given as input, take the first one that's not locked
    # in the media folder.
    wav_list = get_wav_list(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))

    # try to get the position of current wav in list
    try:
        wav_index = wav_list.index(wav_name)

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
        # if wav doesn't exist, go to error page
        return redirect(url_for('error_page'))

    # get percentage of treated files for progress bar
    progress = round(( (float(wav_index) + 1) / len(wav_list) ) * 100)

    # labels that can be put to the segment
    entries = task2choices[task]

    # apply changes to RTTM and put lock to notify the use this file has been
    # treated
    correction = request.form.getlist('trs_label')

    # extract description from wav name
    original_wav = "_".join(wav_name.split('_')[0:-3])
    wav_len = float(wav_name.split('_')[-2])
    #label = wav_name.split('_')[-1].split('.')[0]
    on_off = wav_name.split('_')[-3]
    label = get_label(original_wav, on_off, 'CHI')

    descriptors = [original_wav, wav_len, label, on_off]

    # Check if file has already been seen
    locks = os.listdir(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))

    # remove first dot and .lock, to match names with wav
    locks = [fin[1:-5] for fin in locks if fin.endswith('lock')]
    if wav_name in locks:
        lock = "yes"
    else:
        lock = "no"

    # if some corrections have been made,  change the rttm and go to next page
    if "Do Not Change Annotation" in correction:
        correction = []
        lock_file(wav_name)
        if next_wav:
            return redirect(url_for('treat_all_wavs', wav_name=next_wav))
        else:
            return redirect(url_for('success'))

    if len(correction) > 0:
        rttm_name = original_wav + '.rttm'
        rttm_in = os.path.join(app.root_path, 'static', 'audio', rttm_name)

        modify_rttm(rttm_in, descriptors, correction)
        lock_file(wav_name)
        if next_wav:
            return redirect(url_for('treat_all_wavs', wav_name=next_wav))
        else:
            return redirect(url_for('success'))



    return render_template('show_entries.html', entries=entries,
                           wav=wav_name, next_wav=next_wav, prev_wav=prev_wav,
                           progress=progress, descriptors=descriptors,
                           lock=lock)


@app.route('/success')
def success():
    """ Go to this page after all the files are treated"""
    return render_template('success.html')

@app.route('/error')
def error_page():
    return render_template('error_page.html')
