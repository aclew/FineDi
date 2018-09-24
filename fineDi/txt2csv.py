import pandas as pd
import cPickle
import sys

data_file = sys.argv[1]
sum_file = sys.argv[2]
output = '/'.join(data_file.split('/')[:-1]+['info_dict.csv'])
# output_time = '/'.join(data_file.split('/')[:-1]+['info_dict_time.csv'])
output_is_child = '/'.join(data_file.split('/')[:-1]+['is_child.csv'])


def get_info_from_wavname(wavname, ext = False):
    if wavname[0].isdigit():
        lang = "english"
    else :
        lang = "tsimane"

    features = wavname.split("_")
    if ext :
        features = wavname.strip(".wav").split("_")
    id = features[0]
    age = features[1]
    onset = float(features[2])
    offset = float(features[3])
    return lang, id, age, onset, offset



''' INTERMEDIARY FILE (IS_CHILD) '''
with open(sum_file, "rb") as reading_file:
    sumdict = cPickle.load(reading_file)

is_child_df = pd.DataFrame(columns=['lang', 'id', 'age', 'onset', 'offset', 'length', 'is_child', 'is_not_child'])
total_passes = 0
for k in sumdict.keys():
    if len(sumdict[k])>1: # comes from whole segment
        answers = float(sumdict[k][1] - sumdict[k][0]*10) # can be 3, 1, -1, -3 - all agree is child, all but one agree, all but one agree not child, all agree not child
        # is_child = (answers - 27)/2 # WARNING will give a weird answer if some answers are missing
        total_passes += sumdict[k][0]
        is_child = 0.5 * answers + 1.5
        is_not_child = -0.5 * answers + 1.5
        lang, id, age, onset, offset = get_info_from_wavname(k, True)
        is_child_df.loc[len(is_child_df)] = [lang, id, age, onset, offset, offset-onset, is_child, is_not_child]

is_child_df.to_csv(output_is_child, index=False)

print(total_passes)

''' FINAL FILE (COMPARISON) '''
with open(data_file,"rb") as reading_file:
    newdict = cPickle.load(reading_file)

# output_df = pd.DataFrame(columns=['name', 'mode', 'classif', 'freq'])
output_df = pd.DataFrame(columns=['lang', 'id', 'age', 'onset', 'offset', 'length', 'mode', 'classif', 'count'])
# time_df = pd.DataFrame(columns=['name', 'mode', 'time'])

for k in newdict.keys():
    if k[1]=='is_child':
        pass
    if k[2]=='time':
        pass
        # (name, mode) = k
        # time = newdict[k]
        # time_df.loc[len(time_df)] = [name, mode, time]
        # pass
    else:
        (name, mode, classif) = k
        lang, id, age, onset, offset = get_info_from_wavname(name)
        count = newdict[k]
        output_df.loc[len(output_df)] = [lang, id, age, onset, offset, offset-onset, mode, classif, count]

output_df.to_csv(output, index=False)
# time_df.to_csv(output_time, index=False)
