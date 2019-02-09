"""  2) Calculate expenditure weights on percentile level. 

    i)    Prepare expenditure files first, only keep one month-year combination.
    ii)   Merge income percentiles to expenditure file for given month-year. 
    iii)  Merge CPI data and drop non-merged expenditures.
    iv)   Apply sampling weights to expenditures
    v)    Calculate shares.
   

    d_percentiles is the data set that results from running file CEX_DATA_percentiles. 

 """
import pandas as pd
import numpy as np
 
###############################################################################

#------------------------------------------------------------------------
## Loading and merging data sets. 
#------------------------------------------------------------------------
 
data = pd.read_csv('../original_data/CEX_Data/mtbi961x.csv')
data_12_1995=data[data['REF_MO']==12 ]
data_12_1995=data_12_1995[['NEWID', 'UCC', 'COST']]
data_12_1995.index= range(len(data_12_1995))

# read in percentiles
d_percentiles = pd.read_pickle('../out_data_mngment/Percentiles/12_1995')

# merge percentiles to expenditure data
data_12_1995=data_12_1995.merge(d_percentiles, left_on= 'NEWID', right_on= 'NEWID', how= 'left', validate='m:1', indicator='source')
# drop households without a percentile
data_12_1995=data_12_1995[['NEWID', 'UCC', 'COST', 'FINLWT21', 'Percentile']][data_12_1995['source']=='both']

#------------------------------------------------------------------------
##  Add UCC code description.
#------------------------------------------------------------------------

CE_dic = pd.read_excel('../CEX_Data_Documentation/CE_dictionary.xlsx', sheet_name=2, usecols= "A:E")

CE_dic = CE_dic[CE_dic.File=='MTBI'] # this is only in the Interview survey
CE_dic = CE_dic[ CE_dic.VariableName == 'UCC' ]
CE_dic.CodeValue=CE_dic.CodeValue.astype(int)
CE_dic=CE_dic[['CodeValue', 'CodeDescription']]

data_12_1995=data_12_1995.merge(CE_dic, left_on= 'UCC', right_on= 'CodeValue', how= 'left', indicator= 'source')

# only keep those expenditures with a description

data_12_1995=data_12_1995[[ 'UCC', 'COST', 'FINLWT21', 'Percentile', 'CodeDescription']][data_12_1995.source=='both']

# calculate weighted expenditures

data_12_1995['Weighted_exp']= data_12_1995['COST']*data_12_1995['FINLWT21']

data_12_1995[[ 'UCC', 'Percentile', 'Weighted_exp', 'CodeDescription']].to_pickle('../out_data_mngment/CEX_output/data_12_1995')

