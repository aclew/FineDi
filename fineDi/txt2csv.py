import pandas as pd
import cPickle
import sys

data_file = sys.argv[1]
output = '/'.join(data_file.split('/')[:-1]+['info_dict.csv'])

with open(data_file,"rb") as reading_file:
    newdict = cPickle.load(reading_file)

output_df = pd.DataFrame(columns=['name', 'mode', 'classif', 'freq'])

for k in newdict.keys():
    (name, mode, classif) = k
    freq = newdict[k]
    output_df.loc[len(output_df)] = [name, mode, classif, freq]

output_df.to_csv(data_file.split('.')[0]+'.csv', index=False)
