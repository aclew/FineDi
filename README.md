# FineDi
Diarization Refinement Tool
==========================

This tool allows the user to attribute/check the Vocal Maturity for each key child vocalization in the corpus, and add/correct the labels.

Several routines are available. The main one is to treat all at once all the segments from speaker "CHI" (who is the key child), from all the wav files available. 
The user has to go over each segment, can listen to the segment, and change the labels in a way that he feels is better.
This routine can be quite long, so the user can stop at any time and pick up where they left off.

The GUI is based on the Flask Python web app.

Installation
------------
First you need to install sox if you don't have it, as it is necessary to run the app. On ubuntu:
```    sudo apt install sox```
and on macos:
```    brew install sox```
Then, too install the application, a simple:
```    pip install --editable .```
should suffice (don't forger the dot at the end of the command !).

If some errors are encountered with this command, please open an issue and try the following:
```    pip install flask
       python setup.py build
       python setup.py develop
```

Usage
-----
## Preparation
First you need to place your wav files and the rttm transcriptions (with the same names !) in the `fineDi/static/audio` folder. On first use, the `fineDi/static/audio` folder might not exist, if so, you can create it.
The output of the system will then be found in the same `fineDi/static/audio` folder, with the same name as the input rttm files, but with `refined_` prepended. For example, if the input is
`      C01_0123_0456.rttm`
the output will be
`      refined_C01_0123_0456.rttm`
Please, place the files to treat (wav + rttm) before starting the app, otherwise you might encounter some errors.

## Starting the App
To use the app, please do:
```    sh launch_app.sh
```
This should launch the flask app and open a firefox window with the index page of the app.
If you encounter an error when firefox opens, please refresh the page as sometimes the index might fail to load the first time. If after refreshing the page still fails, please copy the command output and open an issue.

When the app starts, you'll be presented with three options.
The first one, `start session` allows you to start annotating the segments.
The second one, `continue session` allows you to continue annotating where you left the last time.
The third one, `show info on wavs` gives you, for each wav, the number of segments for each speaker in the input transcription.

## Annotation session
When you choose `start session`, you'll be presented with a task choice. The **vocal maturity** task allows you to check all the key child (called "CHI") vocalisations and assign them a vocal maturity label. The **speaker** task allows you to check that all the speaker labels were correctly attributed. For the annotations, if a vocalisation in the transcription is more than 0.5 seconds long, it will be cut in chunks of 0.5s, so the output `refined_*.rttm` won't have segments longer than 0.5 seconds.

### Vocal Maturity task
When you start the task, you'll be on a page with a progress bar on top, a play button which allows you to listen to the segment, a table giving some informations on the current segment (when it occurs in the complete audio, the current label, and wether or not you already treated this segment), the different label choices, and two arrows to naviguate between segment. 
For this task, you **can** attribute several labels to one segment. You can also listen to the segment many times. After choosing the most appropriate label, click on "send" (or "envoyer" in french), to validate your choice and go to the next segment. If you're not sure or not happy with your choice, you can still come back later using the left arrow at the bottom. If you're unsure, you can also choose "undecided", and if you're okay with the label already assigned (in the "current label" box), you can click on "do not change annotation" to keep it. the "exclude" labels are for segments that you think are not relevent (e.g. the segment is not a vocalization from key child), those segments are kept in the output of this systembut can easily be deleted in postprocessing.
When you treated all the segments, you'll end up on a success page and can go back to the index.

### Speaker task
The speaker task is pretty much the same, but the main differences are that the segments presented are not all from the CHI speaker, and this time you can only choose one label per segment.

## Closing the App
After the firefox window is closed, the flask application should be closed by the script. 
This can be checked by typing in command line:
```    ps```
if you see a line saying "flask", it means the application failed to stop, and you can stop it by typing 
```    kill $flask_pid```
where `$flask_pid` is the pid of the flask process, as seen in the output of `ps`.

If the firefox window doesn't open or if the app fails to run, please open an issue describing
the error you get and copying the output written in command line.

Contribution
------------
If you feel some parts don't work well or you'd like to see implemented a new feature,
you can open an issue.


## TODOS
[x] Give info on current files in data/  
[ ] Allow user to see the segments in each files and select only one segment to treat  
[ ] Allow user to select one on wav file to treat  
