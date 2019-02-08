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

exp_data_12_1995= data_12_1995.groupby(['Percentile','UCC', 'CodeDescription', 'value'], as_index=False).agg({'Weighted_exp':'sum'})

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

# keep relevant values
exp_data_12_1995=exp_data_12_1995[['Percentile', 'UCC', 'share', 'Total_expenditures', 'value', 'CodeDescription' ]].sort_values(['Percentile', 'UCC'])

#------------------------------------------------------------------------
##  Calculate percentile-specific price level
#------------------------------------------------------------------------
#def _cobb_douglas(sigma_points, gammas, a):
# return a * (sigma_points ** gammas).product(axis=1)
 
#------------------------------------------------------------------------
##  Calculate real consumption
#------------------------------------------------------------------------

exp_data_12_1995.to_pickle('../../output_data/final/cex_cpi_shares_12_1995')

#