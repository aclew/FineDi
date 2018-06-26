# global variables for task definition
task = None # current task

talker_lab =  {'key child':'CHI',
               'other child': 'OCH',
               'female adult':'FA',
               'male adult':'MA'}
lab2talker = {'CHI': 'key child',
              'OCH': 'other child',
              'FA': 'female adult',
              'MA': 'male adult'}
vocal_mat_lab = {'crying':"Y", 'laughing':"L", 'non-canonical babbling':"N",
                 'canonical babbling':"C", 'undecided':"U", 'exclude':"X", "do not change annotation":"NCA"}
lab2vocal_mat = {"Y":'crying', "L":'laughing',
                 "N":'non-canonical babbling',
                 "C":'canonical babbling',
                 "U": 'undecided',"X": 'exclude',
                 "NCA":"do not change annotation",
                 "<NA>": "<NA>"}
task2col = {'speaker': 7, 'label': 6}

task2choices = {'speaker': talker_lab,
                'label': vocal_mat_lab}
choices2task = {'speaker': lab2talker,
                'label':lab2vocal_mat}
