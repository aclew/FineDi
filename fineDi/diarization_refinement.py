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
# import ipdb
from collections import defaultdict
import subprocess
from tempfile import mkstemp
from os import remove
from shutil import move
import random
from utils import *
# import global variables
from task import *
import cPickle
import datetime

# create app
app = Flask(__name__) # create the application instance :)
#app.config.from_object(__name__) # load config from this file , flaskr.py
# Load config from an environment variable
app.config.from_envvar('FLASK_CONFIG')


# global media_path
# media_path = os.path.join(app.root_path, app.config['MEDIA_ROOT'])
# global step
# step=0
# global max_steps
# max_steps=10
## TODO global summary and info // or not
global dict_path
dict_path = os.path.join(app.root_path, 'static', 'info_dict.txt')
global summary_path
summary_path = os.path.join(app.root_path, 'static', 'summary.txt')
global cut_length
cut_length = 500
global init_time

global html_renderings
html_renderings = 0
global max_trials
max_trials = 100

global requested_answers
requested_answers = 20
## TODO We need: global time (when is the page loaded vs when is the answer)

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
    # if not already done, pretreat the input rttm to split each
    # vocalization in 0.5s length segments

    # write random order in order_file in media/
    print app.config['TEMP_ROOT']

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

        task = request.form.getlist('task')[0]
        write_task(task)
        if ("wholecut" not in task):
            split_segments_rttm(os.path.join(app.root_path, 'static', 'audio'))
        return redirect(url_for('create_segments', task=task))


    return render_template('choose_column.html')

@app.route('/continue')
def pick_up():
    """ If the user chose to continue, we look at the .lock files
    to check which files were already treated
    """
    #wav_list = get_wav_list(os.path.join(app.root_path,
    #                                     app.config['MEDIA_ROOT']))
    wav_list = read_order()

    locks = os.listdir(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))
                                         ## TODO MODIFIED
    # remove first dot and .lock, to match names with wav
    locks = [fin[1:-5] for fin in locks if fin.endswith('lock')]

    # check matching files in both lists
    untreated = [wav for wav in wav_list if not wav in locks]

    first_wav = untreated[0]

    return redirect(url_for('treat_all_wavs', wav_name=first_wav))

@app.route('/creating/<task>')
def create_segments(task):
    """
        Depending on the chosen task, create all the segments that will be
        examined by the user
    """
    global max_trials
    global requested_answers
    media_path = os.path.join(app.root_path, app.config['MEDIA_ROOT'])
    # Before anything, check if there are files in audio/
    # if not, go to success page
    if ("wholecut" not in task):
        if len(os.listdir(os.path.join(app.root_path, 'static', 'audio'))) == 0:
            return redirect(url_for('no_wavs'))

            # First remove everything in the media folder
            for fin in os.listdir(os.path.join(app.root_path,
                                       app.config['MEDIA_ROOT'])):
                if fin == "task.txt":
                    continue
                else:
                    os.remove(os.path.join(app.root_path,
                                   app.config['MEDIA_ROOT'], fin))

                # Create the audio segments
                if task == "label":
                    first_wav = create_segments_label()
                else:
                    first_wav = create_segments_speaker()

    # shuffle media files
        wav_list = get_wav_list(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))
        # print(wav_list)

    else:
        global dict_path
        global summary_path

        try:
            with open(dict_path,"rb") as reading_file:
                info_dict = cPickle.load(reading_file) #TODO pass instead of this?
        except Exception: # if file does not exist, create it # what about other exception than file error?
            info_dict = create_info_txt(media_path+"/cutdir/"+str(cut_length)+"/", dict_path)
            print("dict")
            print(info_dict)
        try:
            with open(summary_path,"rb") as reading_file:
                sum_dict = cPickle.load(reading_file) #TODO pass instead of this?
        except Exception: # if file does not exist, create it
            sum_dict = create_summary_txt(media_path, summary_path)

        # if 500ms (or other length) labeling
        if ("_c" in task):
        # retrieve already cut wav files
            temp_wav_list = get_wav_list(media_path+'/cutdir/'+str(cut_length)+"/")
            print("length:", len(temp_wav_list))
            temp_wav_list = [w for w in temp_wav_list if w.endswith("_"+str(cut_length)+".wav")] # TODO change if other length (compatibility) to get only those which are 500 (or other length) ms long - never too cautious
            print("length:", len(temp_wav_list))
            wav_list = []
            for w in temp_wav_list:
                if sum_dict[w]<requested_answers : # if some data is missing (eg a wav having been heard fewer times)
                    wav_list.append(w)
                    # sum_dict[w] += 1 ## TODO or hould it be later, when actually writing in info, to prevent not completed sessions?
            wav_list = random.sample(wav_list, min(max_trials, len(wav_list))) # sample either defined nb of wav or left wav
            # result = random.sample(chi_utt, k)
        elif ("_w1" in task):
            wav_list = get_wav_list(media_path+'/cutdir/full/')
            wav_list = random.sample(wav_list, min(max_trials, len(wav_list)))
        else:
            temp_wav_list = get_wav_list(media_path+'/cutdir/full/')
            wav_list = []
            for w in temp_wav_list:
                if (sum_dict[w][1]>0 and sum_dict[w][0]<requested_answers) : # if some data is missing (eg a wav having been heard fewer times)
                    wav_list.append(w)
            wav_list = random.sample(wav_list, min(max_trials, len(wav_list))) # sample either defined nb of wav or left wav
        # based on csv, randomly select [k] 500 chunks and/or [k] whole chunks (?)

    if len(wav_list)==0:
        return redirect(url_for('no_wavs'))

    seed = 50
    random.Random(seed).shuffle(wav_list)
    write_order(wav_list)
    first_wav = wav_list[0]

    ## TODO update time when rendering html

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

    ## TODO update time

    global init_time


    task = read_task()

    # if no wav is given as input, take the first one that's not locked
    # in the media folder.
    #wav_list = get_wav_list(os.path.join(app.root_path,
    #                                     app.config['MEDIA_ROOT']))
    wav_list = read_order()
    # init noChoice to None
    noChoice = None

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
    progress = round(( (float(wav_index)) / len(wav_list) ) * 100)

    # labels that can be put to the segment
    entries = task2choices[task]
    labels = choices2task[task]

    # extract description from wav name
    if task == "speaker":
        # print(wav_name)
        (original_wav, wav_len,
         on_off, old_spkr, new_spkr, label) = get_infos_from_wavname_speaker(wav_name)

        display_spkr = labels[new_spkr]
        speaker = True
    elif task == "label":

        (original_wav, wav_len,
         on_off, label) = get_infos_from_wavname_label(wav_name)
        display_spkr = "key child"
        speaker = None
    else:
        (original_wav, wav_len,
        on_off, label) = get_infos_from_wavname_comparison(wav_name)
        display_spkr = "key child"
        speaker = None
        if "_c" in task:
            wav_len = str(cut_length)

    descriptors = [original_wav, wav_len, display_spkr, label, on_off]

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
    if request.method == 'POST':
        # apply changes to RTTM and put lock to notify the use this file has been
        # treated
        correction = request.form.getlist('trs_label')
        print("computing time delta ", datetime.datetime.now())
        choice_duration = datetime.datetime.now()-init_time


        if "Do Not Change Annotation" in correction:
            correction = []
            lock_file(wav_name)
            if next_wav:
                return redirect(url_for('treat_all_wavs', wav_name=next_wav))
            else:
                return redirect(url_for('success'))

        if len(correction) > 0:
            # get new speaker name, to put in lock
            print entries
            correction = [entries[spkr.lower()] for spkr in correction]

            if task == "speaker":
                cor_spkr = correction[0]
            else:
                cor_spkr = None
            if ("wholecut" not in task):
                rttm_name = "refined_" + original_wav + '.rttm'
                rttm_in = os.path.join(app.root_path, 'static', 'audio', rttm_name)

                modify_rttm(rttm_in, descriptors, correction)

                # lock file
                lock_file(wav_name, cor_spkr)
            else:
                # print(correction)
                global dict_path
                global summary_path
                # TODO update following as sth like
                    # info_sum_update(dict_path, sum_path, task, wav_name, correction[0], choice_duration)"
                # open dict (no matter the task)
                with open(dict_path, 'rb') as reading_file:
                    info_dict = cPickle.load(reading_file)
                # open summary (if child, and nb of time it was seen)
                sum_path = os.path.join(app.root_path, 'static', 'summary.txt')
                with open(sum_path, 'rb') as reading_file:
                    sum_dict = cPickle.load(reading_file)

                if ("_c" in task):
                    info_dict[(get_wav_index(wav_name), 'cut', choices2task["wholecut_c"][correction[0]])] += 1
                    if (info_dict[(get_wav_index(wav_name), 'cut', 'time')]==0):
                        info_dict[(get_wav_index(wav_name), 'cut', 'time')] = choice_duration
                    else:
                        info_dict[(get_wav_index(wav_name), 'cut', 'time')] = info_dict[(get_wav_index(wav_name), 'cut', 'time')] + choice_duration
                    sum_dict[wav_name] += 1
                    print(info_dict)
                elif ("_w2" in task):
                    info_dict[(get_wav_index(wav_name), 'whole', choices2task["wholecut_w2"][correction[0]])] += 1
                    info_dict[(get_wav_index(wav_name), 'whole', 'time')] += choice_duration
                    sum_dict[wav_name][0] += 1
                else :
                    info_dict[(get_wav_index(wav_name), 'whole', 'is_child')] += correction[0]
                    sum_dict[wav_name][1] = correction[0]

                # write changes in dict no matter the task
                with open(dict_path, "wb") as writing_file:
                    cPickle.dump(info_dict, writing_file)
                with open(sum_path, "wb") as writing_file:
                    cPickle.dump(sum_dict, writing_file)

                # TODO end of dictionaries updates

            # check if current segment is the last, if so, redirect to success page
            if (next_wav):
                return redirect(url_for('treat_all_wavs', wav_name=next_wav))
            else:
                return redirect(url_for('success'))
        else:
            noChoice = True
    print(task)
    if ("wholecut" not in task):
        directory = 'media/'
    else :
        directory = 'media/cutdir/'
        if ("_c" in task):
            directory += str(cut_length)+'/'
            # no more unchecked or checked
        # elif ("_w1" in task):
        #     directory += 'whole_unchecked/'
        else:
            directory += 'full/'
    print(wav_name)
    ## TODO update time
    global html_renderings
    if html_renderings%2 == 0 :
        init_time = datetime.datetime.now()
        print("rendering html", datetime.datetime.now())
    html_renderings+=1
    return render_template('show_entries.html', entries=entries.keys(),
                           wav=wav_name, dir=directory, next_wav=next_wav, prev_wav=prev_wav,
                           progress=progress, descriptors=descriptors,
                           lock=lock, speaker=speaker, noChoice=noChoice)


@app.route('/success')
def success():
    """ Go to this page after all the files are treated"""
    return render_template('success.html')

@app.route('/nowavs')
def no_wavs():
    """ Go to this page if no wavs were detected"""
    return render_template('no_wavs.html')

@app.route('/error')
def error_page():
    return render_template('error_page.html')

@app.route('/avail_wavs')
def avail_wavs():
    """ show the wavs in the data folder,
        and the CHI segments available inside
    """
    # get list of wavs
    wav_list = get_wav_list(os.path.join(app.root_path, 'static', 'audio'))

    # get info for each wav
    segment = dict()
    for wav_name in wav_list[:]:
        wav_rttm_dict = read_rttm(wav_name)
        infos = [(key, len(wav_rttm_dict[key])) for key in wav_rttm_dict]
        segment[wav_name] = infos

    return render_template('available_wavs.html',
                           wav_list=wav_list, seg=segment)
