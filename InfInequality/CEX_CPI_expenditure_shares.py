"""
Calculate shares
"""
import pandas as pd
import numpy as np

#------------------------------------------------------------------------
## Read in data
#------------------------------------------------------------------------


data_12_1995=pd.read_pickle('../../output_data/CEX_output/exp_cpi_12_1995')

#------------------------------------------------------------------------
## Collapse data set on percentile level
#------------------------------------------------------------------------

exp_data_12_1995= data_12_1995.groupby(['Percentile','UCC', 'CodeDescription'], as_index=False).agg({'Weighted_exp':'sum'})

#------------------------------------------------------------------------
## Calculate total expenditure per percentile
#------------------------------------------------------------------------

exp_data_12_1995_total =exp_data_12_1995.groupby(['Percentile'], as_index=False).agg({'Weighted_exp':'sum'})
exp_data_12_1995_total.columns=['Percentile', 'Total_expenditures']

exp_data_12_1995=exp_data_12_1995.merge(exp_data_12_1995_total, left_on= 'Percentile', right_on= 'Percentile', how= 'left', validate="m:1", indicator= 'source')

#------------------------------------------------------------------------
##  Calculate shares on UCC-Percentile level. 
#------------------------------------------------------------------------
   
exp_data_12_1995['share'] =pd.Series(data=exp_data_12_1995['Weighted_exp'].values/exp_data_12_1995['Total_expenditures'].values)

#------------------------------------------------------------------------
##  Save data set.   
#------------------------------------------------------------------------
                    
exp_data_12_1995=exp_data_12_1995[['Percentile', 'UCC', 'Share', 'CodeDescription']].sort_values(['Percentile', 'UCC'])
exp_data_12_1995.to_pickle('../../output_data/final/cex_cpi_shares_12_1995')

