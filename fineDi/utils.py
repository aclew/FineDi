import os
import subprocess
from tempfile import mkstemp
from os import remove
from shutil import move
from collections import defaultdict
from flask import current_app as app
import flask
import random
import numpy as np
from task import *
import cPickle
import os

def split_segments_rttm(folder):
    """ get all the rttm in folder, and for each folder,
        split each vocalization into small 0.5s long segments
        and write it into folder, with 'refined' prepended to
        the rttm name"""
    all_files = os.listdir(folder)
    # print(all_files)
    all_rttm = [rttm for rttm in all_files if (rttm.endswith('.rttm') and not rttm.startswith('refined'))]
    for rttm in all_rttm:
        with open(os.path.join(folder, rttm), 'r') as fin:
            with open(os.path.join(folder,
                               '_'.join(['refined',rttm])), 'w') as fout:
                rttm_seg = fin.readlines()
                for line in rttm_seg:
                    speak, fname, one, on, dur, ortho, lab, spkr, chnl = line.strip('\n').split('\t')
                    # if dur > 0.5, split line in multiple line of 0.5s length
                    on = float(on)
                    dur = float(dur)
                    if dur > 0.5:
                        last_onset = on + np.floor(dur/0.5) * 0.5 - 0.5
                        for onset in np.linspace(on, last_onset - 0.5, np.floor(dur/0.5) -1):
                            fout.write(u'{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(speak, fname, one, onset, 0.5, ortho, lab, spkr, chnl))
                        last_dur = (on + dur) - last_onset
                        fout.write(u'{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(speak, fname, one, last_onset , last_dur, ortho, lab, spkr, chnl))

                    else:
                        fout.write(u'{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(speak, fname, one, on, dur, ortho, lab, spkr, chnl))
    return


def get_wav_list(folder):
    """ Get all the wav files in the static folder
        and return them as a list.
        Useful when routine used is to treat all the wavs.
    """
    all_files = os.listdir(folder)
    return [wav for wav in all_files if wav.endswith('.wav')]

def write_order(wav_list):
    """ write the random order of the wavs in a text file"""
    with open(os.path.join(app.root_path, app.config['MEDIA_ROOT'], "order.txt"), 'w') as fout:
        for wav_name in wav_list:
            fout.write(u'{}\n'.format(wav_name))
    return

def read_order():
    """ read the random order of the wavs"""
    with open(os.path.join(app.root_path, app.config['MEDIA_ROOT'], "order.txt"), 'r') as fin:
        order = fin.readlines()
        wav_list = []
        for line in order:
            wav_list.append(line.strip('\n'))
    return wav_list

def lock_file(wav_name, spkr_name=None):
    """ When a file is treated, write a .<wav_name>.lock file in the media
        folder to avoid retreating the same files twice
    """
    lock_file = ".{}.lock".format(wav_name)

    # create empty lock file ##TODO add date in lock file ?
    with open(os.path.join(app.root_path,
                      app.config['MEDIA_ROOT'],
                      lock_file), 'w') as fout:
        if spkr_name:
            fout.write(u'{}'.format(spkr_name))
    return

def get_label(wav_name, cur_on, cur_spkr):
    """ Get the current label for the wav file being treated"""
    rttm = os.path.join(app.root_path, 'static', 'audio','refined_' + wav_name + '.rttm')
    print(rttm)
    with open(rttm, 'r') as fin:
        annot = fin.readlines()
        print("annotating")
        for line in annot:
            _1, fname, _2, on, dur, _3, label, spkr, _4 = line.strip('\n').split('\t')
            # print(fname, wav_name, float(on), float(cur_on), spkr, cur_spkr)
            if ( (fname == wav_name) and
                 (float(on) == float(cur_on)) and
                 (spkr == cur_spkr)):
                split_label = label.split(',')
                out_label = ','.join([lab2vocal_mat[lab] for lab in split_label])
    return out_label


def modify_rttm(rttm_in, descriptors, correction):
    """ Change only one line in RTTM file, using the labels
        entered by the user
    """
    ### Reminder, descriptors is:
    # [original_wav, wav_len, display_spkr, label, on_off]
    # get which column should be changed
    task = read_task()
    col_to_change = task2col[task]
    labels = choices2task[task]
    speakers = talker_lab

    # create dict to store input and output columns of RTTM files
    in_col = dict()
    out_col = dict()

    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(rttm_in) as old_file:
            for line in old_file:
                (in_col[0], in_col[1], in_col[2],
                 in_col[3], in_col[4], in_col[5],
                 in_col[6], in_col[7], in_col[8]) = line.strip('\n').split('\t')
                if  ((in_col[1] == descriptors[0]) and
                     (float(in_col[3]) == float(descriptors[4])) and
                     (in_col[7] == speakers[descriptors[2]])):
                    # write correction in correct column
                    for key in in_col:
                        if key == col_to_change:
                            out_col[key] = ','.join(correction)
                        else:
                            out_col[key] = in_col[key]
                    #line = '\t'.join([_1, fname, _2, on, dur,
                    #                  _3, ','.join(correction), spkr,
                    #                  _4 + '\n'])
                    line = '\t'.join([out_col[0], out_col[1], out_col[2],
                                      out_col[3], out_col[4], out_col[5],
                                      out_col[6], out_col[7],
                                      out_col[8] + '\n'])

                new_file.write(line)

    #Remove original file
    remove(rttm_in)
    #Move new file
    move(abs_path, rttm_in)


def get_infos_from_wavname_label(wav_name, rttm=True): # remove rttm
    """
        when the segments are created, some key infos are
        put in the name of the wav file.
        This function retrieves these infos
    """
    original_wav = "_".join(wav_name.split('_')[0:-3])
    wav_len = float(wav_name.split('_')[-2])
    #label = wav_name.split('_')[-1].split('.')[0]
    on_off = wav_name.split('_')[-3]
    label = "None"
    if rttm:
        label = get_label(original_wav, on_off, 'CHI')
    return original_wav, wav_len, on_off, label


def get_infos_from_wavname_comparison(wav_name):
    original_wav = wav_name
    onset = wav_name.split('_')[-2]
    offset = wav_name.split('_')[-1].strip('.wav')
    wav_len = str(float(offset)-float(onset))
    label = "None"
    return original_wav, wav_len, onset, label

def get_infos_from_wavname_speaker(wav_name):
    """
        when the segments are created, some key infos are
        put in the name of the wav file.
        This function retrieves these infos
    """
    print(wav_name)
    original_wav = "_".join(wav_name.split('_')[0:-3])
    wav_len = float(wav_name.split('_')[-2])
    #label = wav_name.split('_')[-1].split('.')[0]
    on_off = wav_name.split('_')[-3]
    old_spkr = wav_name.split('_')[-1].split('.')[0]

    # To get label, we should check if the file has already been seen.
    # If so, it means the speaker has changed and we should get the
    # current speaker
    locks = os.listdir(os.path.join(app.root_path,
                                         app.config['MEDIA_ROOT']))

    # remove first dot and .lock, to match names with wav
    locks = [fin[1:-5] for fin in locks if fin.endswith('lock')]
    if wav_name in locks:
        with open(os.path.join(app.root_path, app.config['MEDIA_ROOT'],
                               '.' + wav_name + ".lock"), 'r') as fin:
            new_spkr = fin.read().strip('\n')

    else:
        new_spkr = old_spkr
    print(original_wav, on_off, new_spkr)
    label = get_label(original_wav, on_off, new_spkr)
    return original_wav, wav_len, on_off, old_spkr, new_spkr, label

#def read_rttm(wav_name):
#    """ read the transcription associated to <wav_name>
#        and create a dict that returns the list of intervals and the
#        label associated with this interval for each speaker in the corpus.
#    """
#
#    rttm = wav_name.split('.')[0] + '.rttm'
#    trs = defaultdict(list)
#
#    # read the rttm and create dict {spkr -> segments w/ label }
#    with open(rttm, 'r') as fin:
#        annot = fin.readlines()
#        trs = dict()
#        for line in annot:
#            _, spkr, _, on, dur, _, _, label, _ = line.strip('\n').split('\t')
#            trs[spkr].append((float(on), float(on) + float(dur),
#                              label))
#    return trs

def read_rttm(wav_name):
    """ read the transcription associated to <wav_name>
        and create a dict that returns the list of intervals and the
        label associated with this interval for each speaker in the corpus.
    """

    rttm = 'refined_' + wav_name.split('.')[0] + '.rttm'
    trs = defaultdict(list)

    # read the rttm and create dict {spkr -> segments w/ label }
    with open(os.path.join(app.root_path, 'static', 'audio', rttm), 'r') as fin:
        annot = fin.readlines()
        for line in annot:
            _, fname, _, on, dur, _, _, spkr, label = line.strip('\n').split('\t')
            trs[spkr].append((float(on), float(dur),
                              label))
    return trs

def write_task(task):
    """
        Write a task.txt file containing only the name of the task
        in the Media folder, so that when the usercontinues the task,
        the session knows what task it is.
    """
    with open(os.path.join(app.root_path, app.config['MEDIA_ROOT'], "task.txt"), 'w') as fout:
        fout.write(u'{}'.format(task))
    return

def read_task():
    """
        Read the task.txt file containing the
        current task
    """
    with open(os.path.join(app.root_path, app.config['MEDIA_ROOT'], "task.txt"), 'r') as fin:
        task = fin.read().strip('\n')
    return task


def create_segments_speaker():
    """ Take each wav, retrieve all the annotated segments,
        cut the wav into the segments corresponding to each speaker.
        The names of the outputed wavs are :
            in_wav_on_off_spkr_lab_originalSpeaker.wav
        where in_wav is the input wav that is segmented, on is
        the time when the segment starts, off the time when the
        segment ends, spkr is the name of the speaker and label
        is the annotation associated with this speaker

    """
    # start by removing all the wavs in the media folder
    # first get all the wavs

    wav_list = get_wav_list(os.path.join(app.root_path, 'static', 'audio'))
    print(wav_list)
    # for each wav, retrieve the labels
    for wav_name in wav_list[:]:
        wav_rttm_dict = read_rttm(wav_name)
        # iterate over all the speakers in the RTTM
        for key in wav_rttm_dict:
            for on, dur, lab in wav_rttm_dict[key]:
                wav_path = os.path.join(app.root_path, 'static',
                                        'audio', wav_name)
                # skip empty segments
                if dur <= 0:
                    continue

                # define output wav path
                output_wav = wav_name.split('.')[0] + '_{}_{}_{}_{}.wav'.format(on, dur,
                                                                                lab, key)
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
    return first_wav


def create_segments_label():
    """ Take each wav, retrieve all the annotated segments,
        cut the wav into the segments corresponding to 'CHI'
        and check the labels.
        The names of the outputed wavs are :
            in_wav_on_off_lab.wav
        where in_wav is the input wav that is segmented, on is
        the time when the segment starts, off the time when the
        segment ends, spkr is the name of the speaker and label
        is the annotation associated with this speaker

    """
    # start by removing all the wavs in the media folder
    # first get all the wavs
    wav_list = get_wav_list(os.path.join(app.root_path, 'static', 'audio'))

    # for each wav, retrieve the labels
    for wav_name in wav_list[:]:
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
    return first_wav

def get_wav_index(wav_name):
    # considering the name of the file is sth like child_age_onset_offset
    res = '_'.join(wav_name.split('.')[0].split('_')[0:4])
    return res

def create_info_txt(media_path, dict_path):
    info_dict = {}
    all_files = [f for f in os.listdir(media_path) if f.endswith(".wav")]
    for f in all_files:
        for mode in modes:
            info_dict[(get_wav_index(f), mode, 'time')]=0
            for mat in vocal_mat_lab_cut.keys():
                info_dict[(get_wav_index(f), mode, mat)] = 0
        info_dict[(get_wav_index(f), 'whole', 'is_child')] = 0
    with open(dict_path, "wb") as writing_file:
        cPickle.dump(info_dict, writing_file)
    return info_dict

def create_summary_txt(media_path, summary_path):
    sum_dict = {}
    files_500 = [f for f in os.listdir(media_path+'/cutdir/500/') if (f.endswith(".wav"))] ## TODO change path !!!!!
    files_full = [f for f in os.listdir(media_path+'/cutdir/full/') if (f.endswith(".wav"))] # TODO change path + change to files_full
    for f in files_500:
        sum_dict[f] = 0 # if it is 500, only checking number of times it was seen
    for f in files_full:
        sum_dict[f] = [0,0] # if full, sun_dict[1] = -1 if not child, +1 if child, and if so, sum_dict[0] = nb of times seen
    with open(summary_path, "wb") as writing_file:
        cPickle.dump(sum_dict, writing_file)
    return sum_dict
