""" This file is to bring consumption shares and price data together. """

""" We have a file  with the expenditure shares on percentile-month/year-UCC level.
    And a file containing CPI data on quarterly level. 
"""
import pandas as pd
import numpy as np

#------------------------------------------------------------------------
## Read in Data.
#------------------------------------------------------------------------

d_exp_12_1995 = pd.read_pickle('../../original_data/shares/12_1995')
d_CPI = pd.read_pickle('../../original_data/CPI_prepared/CPI_m')
concordance = pd.read_pickle('../../original_data/Concordance/concordance_final')

#------------------------------------------------------------------------
## Concordance between UCC and CPI series-id.
#------------------------------------------------------------------------

f=pd.Series(d_exp_12_1995.UCC.unique()).sort_values( na_position= 'first')
g = pd.Series(d_CPI.unique()).sort_values( na_position= 'first')