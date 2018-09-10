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
task2col = {'speaker': 7, 'label': 6}

task2choices = {'speaker': talker_lab,
                'label': vocal_mat_lab,
                'wholecut': vocal_mat_lab_cut}
choices2task = {'speaker': lab2talker,
                'label': lab2vocal_mat,
                'wholecut': lab2vocal_mat_cut}

# maturity = ['crying', 'laughing', 'canonical', 'non-canonical', 'exclude', 'undecided']
modes = ['cut', 'whole']
