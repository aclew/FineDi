import pandas as pd
import cPickle
import sys

data_file = sys.argv[1]
output = '/'.join(data_file.split('/')[:-1]+['info_dict.csv'])

with open(data_file,"rb") as reading_file:
    newdict = cPickle.load(reading_file)

output_df = pd.DataFrame(columns=['name', 'mode', 'classif', 'freq'])
time_df = pd.DataFrame(columns=['name', 'mode', 'time'])

for k in newdict.keys():
    if k[1]=='is_child':
        pass
    if k[2]=='time':
        (name, mode) = k
        time = newdict[k]
        time_df.loc[len(time_df)] = [name, mode, time]
        pass
    else:
        (name, mode, classif) = k
        freq = newdict[k]
        output_df.loc[len(output_df)] = [name, mode, classif, freq]

output_df.to_csv(data_file.split('.')[-1]+'.csv', index=False)
time_df.to_csv(data_file.split('.')[-1]+'-time.csv', index=False)
