# FineDi
Diarization Refinment Tool
==========================

This tool allows the user to check the diarization for each child segment in the corpus, and add/correct the labels.

Several routines are available. The main one is to treat all at once all the segments from speaker "CHI" (who is the main child), from all the wav files available. 
The user has to go over each segment, can listen to the segment, and change the labels in a way that he feels is better.
This routine can be quite long, so the user can stop at any time and pick up where they left offi.

The GUI is based on the Flask Python web app.

Installation
------------
First you need to install sox if you don't have it, as it is necessary to run the app. On ubuntu:
```    sudo apt install sox```
and on macos:
```    brew install sox```
Then, too install the application, a simple:
```    pip install --editable .```
should suffice.
If some errors are encountered with this command, please open an issue and try the following:
```    pip install flask
       python setup.py build
       python setup.py develop
```

Usage
-----
First you need to place your wav files and the rttm transcriptions (with the same names !) in the `fineDi/static/audio` folder. Please note that the `.rttm` will be modified directly, so if you feel unsure, please make a backup of those files.

To use the app, please do:
```    sh launch_app.sh
```
This should launch the flask app and open a firefox window with the index page of the app.
After the firefox window is closed, the flask application should be closed by the script. 
This can be checked by:
```    ps```

If the firefox window doesn't open or if the app fails to run, please open an issue describing
the error you get.

Contribution
------------
If you feel some parts don't work well or you'd like to see implemented a new feature,
you can open an issue.


## TODOS
[X] ask user f they want to continue where they left off, or treat all the files
[ ] allow user to choose which field they want to treat (label or speaker)
[X] put lock on treated files to avoid treating the same file twice
[X] go to next page when validating the form
[ ] Give info on current files in data/
[ ] Allow user to see the segments in each files and select only one segment to treat
[ ] Allow user to select one on wav file to treat
