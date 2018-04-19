import os
import subprocess
from tempfile import mkstemp
from os import remove
from shutil import move
from collections import defaultdict
from flask import current_app as app

def get_wav_list(folder):
    """ Get all the wav files in the static folder
        and return them as a list.
        Useful when routine used is to treat all the wavs.
    """
    all_files = os.listdir(folder)
    return [wav for wav in all_files if wav.endswith('.wav')]

def lock_file(wav_name):
    """ When a file is treated, write a .<wav_name>.lock file in the media folder
        to avoid retreating the same files twice
    """
    lock_file = ".{}.lock".format(wav_name)
    
    # create empty lock file ##TODO add date in lock file ?
    open(os.path.join(app.root_path,
                      app.config['MEDIA_ROOT'],
                      lock_file), 'w').close
    return

def get_label(wav_name, cur_on, cur_spkr):
    """ Get the current label for the wav file being treated"""
    rttm = os.path.join(app.root_path, 'static', 'audio', wav_name + '.rttm')
    with open(rttm, 'r') as fin:
        annot = fin.readlines()
        for line in annot:
            _1, fname, _2, on, dur, _3, label, spkr, _4 = line.strip('\n').split('\t')
            if ( (fname == wav_name) and
                 (float(on) == float(cur_on)) and
                 (spkr == cur_spkr)):
                out_label = label
    return out_label


def modify_rttm(rttm_in, descriptors, correction):
    """ Change only one line in RTTM file, using the labels
        entered by the user
    """

    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(rttm_in) as old_file:
            for line in old_file:
                _1, fname, _2, on, dur, _3, label, spkr, _4 = line.strip('\n').split('\t')
                if  ((fname == descriptors[0]) and
                     (float(on) == float(descriptors[3])) and
                     (spkr == "CHI")):
                    line = '\t'.join([_1, fname, _2, on, dur,
                                      _3, ','.join(correction), spkr,
                                      _4 + '\n'
                
                new_file.write(line)

    #Remove original file
    remove(rttm_in)
    #Move new file
    move(abs_path, rttm_in)

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


