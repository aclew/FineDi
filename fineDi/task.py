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
                 'canonical babbling':"C", 'vegetative':'V', 'undecided':"U",
                 'exclude':"X", "do not change annotation":"NCA"}
vocal_mat_lab_cut = {'crying':"Y", 'laughing':"L", 'non-canonical babbling':"N",
                 'canonical babbling':"C", 'vegetative':'V', 'exclude':"X", 'undecided':"U"}
vocal_mat_lab_is_child = {"keep (key child)" : 1, "exclude (not key child)" : -1}

lab2vocal_mat = {"Y":'crying', "L":'laughing',
                 "N":'non-canonical babbling',
                 "C":'canonical babbling',
                 "V": 'vegetative',
                 "U": 'undecided',"X": 'exclude',
                 "NCA":"do not change annotation",
                 "<NA>": "<NA>"}
lab2vocal_mat_cut = {"Y":'crying', "L":'laughing',
                 "N":'non-canonical babbling',
                 "C":'canonical babbling',
                 "V": 'vegetative',
                 "X": 'exclude',
                 "U": 'undecided',
                 "<NA>": "<NA>"}
lab2vocal_mat_is_child = {1 : "keep (key child)", -1 : "exclude (not key child)"}
task2col = {'speaker': 7, 'label': 6}

task2choices = {'speaker': talker_lab,
                'label': vocal_mat_lab,
                'wholecut_c': vocal_mat_lab_cut,
                'wholecut_w1': vocal_mat_lab_is_child,
                'wholecut_w2': vocal_mat_lab_cut}
choices2task = {'speaker': lab2talker,
                'label': lab2vocal_mat,
                'wholecut_c': lab2vocal_mat_cut,
                'wholecut_w1': lab2vocal_mat_is_child,
                'wholecut_w2': lab2vocal_mat_cut}
instructions = {'wholecut_c': "Listen to the audio clip by clicking on the play button. Choose the label that fits best what you hear (please only choose one option). When your choice is made, click on 'Submit Query' to go to the next file.",
'wholecut_w1': "Listen to the audio clip by clicking on the play button. If what you hear is definitely the child being recorded and no one else, then check the box for 'Keep', otherwise, check the box for 'Exclude'. \n \n Select only one option, and when your choice is made, click on 'Submit Query' to go to the next file.",
'wholecut_w2': "Listen to the audio clip by clicking on the play button. Choose the label that fits best what you hear (please only choose one option). When your choice is made, click on 'Submit Query' to go to the next file."}
# maturity = ['crying', 'laughing', 'canonical', 'non-canonical', 'exclude', 'undecided']
modes = ['cut', 'whole']
