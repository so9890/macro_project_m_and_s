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

#------------------------------------------------------------------------
## Keep Price information for respective month-year of expenditures.
#------------------------------------------------------------------------

d_CPI_12_1995 = d_CPI[d_CPI['year']== 1995 ]
d_CPI_12_1995 =d_CPI_12_1995[['series_id', 'value', 'Description', 'UCC']][d_CPI_12_1995.period.str.contains('12')]

#------------------------------------------------------------------------
## Merge CPI data set to expenditure data. 
#------------------------------------------------------------------------
#verify UCCs are integers in both files
d_exp_12_1995['UCC']=d_exp_12_1995['UCC'].astype(int)
d_CPI_12_1995['UCC']=d_CPI_12_1995['UCC'].astype(int)
d_exp_12_1995=d_exp_12_1995.merge(d_CPI_12_1995,  left_on= 'UCC', right_on= 'UCC', how= 'left')

#------------------------------------------------------------------------
## Use second concordance file from WS to match non-merged items. 
# split merged expenditure file into merged and non_merged. 
#------------------------------------------------------------------------

not_merged=d_exp_12_1995[['Percentile', 'UCC', 'Share', 'CodeDescription']][pd.isna(d_exp_12_1995.Description)]
print(len(not_merged.drop_duplicates('UCC')), 'UCCs could not be merged with BLS concordance.')
# the reason is that those unmerged UCCs are not in the CPI file from 12_1995!

# also keep all merged UCCs that will be used to append data set later.
merged= d_exp_12_1995[['Percentile', 'UCC', 'Share', 'CodeDescription', 'series_id', 'value',
       'Description']][~pd.isna(d_exp_12_1995.Description)]

#------------------------------------------------------------------------
## Use the concordance file from William Casey to match so far unmatched UCCs.
## to derive this save a copy of the non_merged UCCs
#------------------------------------------------------------------------

d_CPI_WC = pd.read_pickle('../../original_data/CPI_prepared/CPI_m_WC')

# keep relevant periods only
d_CPI_WC_12_1995 = d_CPI_WC[d_CPI_WC['year']== 1995 ]
d_CPI_WC_12_1995 =d_CPI_WC_12_1995[['series_id', 'value', 'Description', 'UCC']][d_CPI_WC_12_1995.period.str.contains('12')]

# ensure UCC in d_CPI_WC is integer
d_CPI_WC_12_1995['UCC']=d_CPI_WC_12_1995['UCC'].astype(int)

not_merged['ID']="NM"
not_merged=not_merged.merge(d_CPI_WC_12_1995,  left_on= 'UCC', right_on= 'UCC', how= 'left')

# some items are still not merged. Why?
not_mergedII=not_merged[['UCC','Description']]

not_mergedII=not_mergedII[pd.isna(not_mergedII.Description)]
print(len(not_mergedII.drop_duplicates('UCC')), 'UCCs could not be merged after \
additional WS concordance. They are not in the CPI data set for the given month-year \
combination. Thus,', len(not_merged.drop_duplicates('UCC'))-len(not_mergedII.drop_duplicates('UCC')), 
'additinal observations merged thanks to WS concordance file.')

#------------------------------------------------------------------------
## Calculate shares from merged items. Such that shares add up to one.
## Otherwise would have prices of zero for goods not in CPI file which would 
## bias the percentile specific CPI.
#------------------------------------------------------------------------

exp_cpi_12_1995=

