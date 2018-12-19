"""
Read in data and prepare dataset

@author: sdobkowitz
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import io

with open(r'C:\Users\sdobkowitz\Desktop\macro_topics\InfInequality\ffile801', 'r') as file:
    content =file.read()

s2= content.replace('  ', ',')
df = pd.read_table(io.StringIO(s2), sep=',', header = None, error_bad_lines= False )




#    print(repr(line))
    
#    line = line.strip()

#columns = line.split()

 dII = pd.read_csv(r'C:\Users\sdobkowitz\Desktop\macro_topics\CEX_Data\intrvw17\fmli171x.csv', header = 0, sep=',' )