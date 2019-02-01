"""  2) Calculate expenditure weights on percentile level. 

    i) Prepare expenditure files first.
       Apply sampling weights.
   ii) Then merge income percentiles to expenditure file for given month-year. 

    d_percentiles is the data set that results from running file CEX_DATA_percentiles. 

 """
import pandas as pd
import numpy as np
 
###############################################################################
""" Loading and merging data sets. """
 
 
data = pd.read_csv('../../data/CEX_Data/intrvw96/mtbi961x.csv')
data_12_1995=data[data['REF_MO']==12 ]
data_12_1995=data_12_1995[['NEWID', 'UCC', 'COST']]
data_12_1995.index= range(len(data_12_1995))

# read in percentiles
d_percentiles = pd.read_pickle('../../data/Percentiles/12_1995')

# merge percentiles
data_12_1995=data_12_1995.merge(d_percentiles, left_on= 'NEWID', right_on= 'NEWID', how= 'left')
# drop households without a percentile
data_12_1995=data_12_1995[~np.isnan(data_12_1995['Percentile'].values)]

###############################################################################
""" Weight expenditures on household level using sampling weights. """


data_12_1995['Weighted_exp']= data_12_1995['COST']*data_12_1995['FINLWT21']


""" Summing up expenditures by Percentile and UCC """

exp_data_12_1995= data_12_1995.groupby(['Percentile','UCC'], as_index=False).agg({'Weighted_exp':['sum']})
exp_data_12_1995.columns = ['Percentile', 'UCC', 'Expenditures']


"""  Total expenditures by percentile"""

exp_data_12_1995_total =exp_data_12_1995.groupby(['Percentile'], as_index=False).agg({'Expenditures':['sum']})
exp_data_12_1995_total.columns=['Percentile', 'Total_expenditures']

exp_data_12_1995=exp_data_12_1995.merge(exp_data_12_1995_total, left_on= 'Percentile', right_on= 'Percentile', how= 'left')

""" Calculate shares on UCC-Percentile level. """

   
exp_data_12_1995['Share'] =pd.Series(data=exp_data_12_1995['Expenditures'].values/exp_data_12_1995['Total_expenditures'].values)
                            
