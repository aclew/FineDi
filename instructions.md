# Instructions

## Setting up the environment for the first time

### 1. Set git

- Open Terminal and clone the repository

  `git clone git@github.com:aclew/FineDi.git ~/Desktop/`

- Check that you are on the right branch

  `git branch -a`

  - If the output does not have `whole_vs_500` in green, do

    `git checkout whole_vs_500`


### 2. Put dataset at the right place

- Go to _FineDi -> fineDi -> static_

  - Check that the files _info_dict.txt_ and _summary.txt_ exist (if not, that's bad)

  - In _FineDi -> fineDi -> static_, create a folder named _media_

  - Copy the folder _Seedlings -> classif_comparison -> cut_dir_ in _media_

## Retrieving changes (if not first time)

- Get the latest modifications to the files _info_dict.txt_ and _summary.txt_

  `git pull`

## Running the app

### 1. Launching the app

- Once the environment is set up, open `Terminal`

- Write `cd ` then drag and drop the FineDi folder in the terminal (the command should look like `cd /Users/gb146/Desktop/FineDi`)

- Check that you are at the right place by writing the following command in the terminal:

  `ls`

You should then see the name `launch_app.sh` appear in the list

- Launch the app from the Terminal

  `sh launch_app.sh`

- Open the corresponding address in Firefox

  - Open Firefox

  - Enter the address `localhost:5000` in the address bar, enter

### 2. Options to choose

- Choose __Start session__

- Click on the task that you want to do (__500, first pass, second pass__)

### 3. Steps to follow

- For __500__ or __second pass__

  - Listen to the clip by clicking the play button

  - Choose a label, then click __Submit query__; this will automatically go to the next wav

- For __first pass__

  - Listen to the clip by clicking the play button

  - Say whether you hear a child or not by clicking __Exclude__ or __Keep__, then click __Submit query__; this will automatically go to the next wav

## Finishing a session

- A progress bar indicates the proportion of files that you heard and the proportion that is left to hear. You will hear a maximum of 100 clips by session. Once the progress bar is full, a success page appears: your task is complete!

  - Quit Firefox

  - In the terminal, press ctrl+C to quit the app

- Save your progress on the git repository:

  - In the terminal, write the commands:

    `git add findeDi/static/summary.txt`

    `git add findeDi/static/info_dict.txt`

    `git commit -m "processed [n] files for task [i]"` (with n the number of files that you listened to and i the name of the task)

    `git push`


You did your part, thank you!
