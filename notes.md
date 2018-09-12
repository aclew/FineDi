### Notes

When creating the segments, only chose 500+ms utterances in cha file

is_child : 0 : not seen yet, 1: true, 2: false


## Architecture for the comparison project

fineDi/static/media/cutdir/

    - info_dict.txt

    - summary.txt

    - 500/ _contains all the 500ms wav files_

        - id_age_onset_offset_500.wav

    - whole_unchecked/ _initially contains all the whole wav files_

        - id_age_onset_offset.wav

    - whole_checked/ _initially empty_

        - id_age_onset_offset.wav

## Different tasks

To start:

- put all the 500ms wav files in the 500 directory (make sure their name ends with \_500.wav) (if directory not existing - __TODO: SOLVE DIRECTORY PROBLEM__)

- put all the full utterance wav files in the whole_unchecked directory


### One pass on 500ms segments

Based on files ending in "\_500.wav"  

Select Create session, whole vs 500 - 500


Each file finishing by "\_500.wav" is considered.

The ones that have already been processed a certain number (fixed at the beginning of the experiment)(info retrieved from summary.txt) of times are dismissed

From those left, a list of min(trial_number, number_of_such_files) wav files is retrieved and reordered randomly.

Each wav file in this list is presented to the user with a set of possible choices. The user's choice is then written in info_dict, and the next wav in the list is processed.

### Two passes, first pass

Based on files in "whole_unchecked"

Select Create session, whole vs 500 - whole, pass 1


All files in whole_unchecked ending with ".wav" are considered

From these, min(trial_number, number_of_such_files) are retrieved and randomly ordered

The user's answer to the question "is this the key child ?" is recorded in info_dict.txt.

If the answer is yes, the file is moved in checked files.

If the answer is no, the extension ".not_CHN" is added to the file (meaning it will not be considered as a wav file anymore)

### Two passes, second pass

Based on files in "whole_checked"

Select Create session, whole vs 500 - whole, pass 1


All files in whole_checked ending with ".wav" are considered

The ones that have already been processed a certain number if times (fixed at the beginning of the experiment)(info retrieved from summary.txt)  are dismissed

From those left, a list of min(trial_number, number_of_such_files) wav files is retrieved and reordered randomly.

Each wav file in this list is presented to the user with a set of possible choices. The user's choice is then written in info_dict, and the next wav in the list is processed.

## Post-processing
