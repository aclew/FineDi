import os
import subprocess
from tempfile import mkstemp
from os import remove
from shutil import move
from collections import defaultdict
from flask import current_app as app
import flask
from task import *

def get_wav_list(folder):
    """ Get all the wav files in the static folder
        and return them as a list.
        Useful when routine used is to treat all the wavs.
    """
    all_files = os.listdir(folder)
    return [wav for wav in all_files if wav.endswith('.wav')]

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
    print wav_name
    rttm = os.path.join(app.root_path, 'static', 'audio', wav_name + '.rttm')
    with open(rttm, 'r') as fin:
        annot = fin.readlines()
        for line in annot:
            _1, fname, _2, on, dur, _3, label, spkr, _4 = line.strip('\n').split('\t')
            #print "file"
            #print fname, wav_name
            #print "onset"
            #print on, cur_on
            #print "speaker"
            #print spkr, cur_spkr
            if ( (fname == wav_name) and
                 (float(on) == float(cur_on)) and
                 (spkr == cur_spkr)):
                out_label = label
    return out_label


def modify_rttm(rttm_in, descriptors, correction):
    """ Change only one line in RTTM file, using the labels
        entered by the user
    """
    # get which column should be changed
    task = read_task()
    col_to_change = task2col[task]

    # create dict to store input and output columns of RTTM files
    in_col = dict()
    out_col = dict()

    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(rttm_in) as old_file:
            print rttm_in
            for line in old_file:
                (in_col[0], in_col[1], in_col[2],
                 in_col[3], in_col[4], in_col[5],
                 in_col[6], in_col[7], in_col[8]) = line.strip('\n').split('\t')
                if  ((in_col[1] == descriptors[0]) and
                     (float(in_col[3]) == float(descriptors[4])) and
                     (in_col[7] == descriptors[2])):
                    # write correction in correct column
                    for key in in_col:
                        if key == col_to_change:
                            print "just put {} in col {} of {}".format(','.join(correction), key+1, rttm_in)
                            out_col[key] = ','.join(correction)
                        else:
                            print "col key {}".format(key)
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


def get_infos_from_wavname_label(wav_name):
    """
        when the segments are created, some key infos are
        put in the name of the wav file.
        This function retrieves these infos
    """
    original_wav = "_".join(wav_name.split('_')[0:-3])
    wav_len = float(wav_name.split('_')[-2])
    #label = wav_name.split('_')[-1].split('.')[0]
    on_off = wav_name.split('_')[-3]
    label = get_label(original_wav, on_off, 'CHI')
    return original_wav, wav_len, on_off, label


def get_infos_from_wavname_speaker(wav_name):
    """
        when the segments are created, some key infos are
        put in the name of the wav file.
        This function retrieves these infos
    """
    original_wav = "_".join(wav_name.split('_')[0:-4])
    wav_len = float(wav_name.split('_')[-3])
    #label = wav_name.split('_')[-1].split('.')[0]
    on_off = wav_name.split('_')[-4]
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

    rttm = wav_name.split('.')[0] + '.rttm'
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
