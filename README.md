# FineDi
Diarization Refinment Tool
==========================

This tool allows the user to check the diarization for each child segment in the corpus, and add/correct the labels.

Several routines are available. The main one is to treat all at once all the segments from speaker "CHI" (who is the main child), from all the wav files available. 
The user has to go over each segment, can listen to the segment, and change the labels in a way that he feels is better.
This routine can be quite long, so the user can stop at any time and pick up where they left off

The GUI is based on the Flask Python web app.
