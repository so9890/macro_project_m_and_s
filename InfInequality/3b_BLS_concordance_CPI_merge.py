""" CPI_CE concordance. """

import pandas as pd
import re
import numpy as np

from functions import _quarter_collapse

#------------------------------------------------------------------------
## Read in CPI and concordance file
#------------------------------------------------------------------------

d_CPI = pd.read_pickle('../../original_data/CPI_prepared/CPI_for_con')
con_bls = pd.read_excel('../../original_data/Concordance/concordance_BLS.xlsx' , header=3, usecols = "A:D")

#------------------------------------------------------------------------
## Con_bls is on ELI level. Since our price level is on Item-stratum level 
## have to aggregate ELIs onitem-stratum level: ie. first 4 digits of ELI 
#------------------------------------------------------------------------

con_bls['item_id']=""
for i in range(0,len(con_bls)):
    con_bls['item_id'].iloc[i]=con_bls.ELI.iloc[i][:4]

# drop duplicates in con_bls in terms of item_stratum_id and UCC
con_bls['dup']=con_bls.duplicated(['UCC', 'item_id'] )
con_bls=con_bls[~con_bls.dup]
con_bls.index=range(0,len(con_bls))

#------------------------------------------------------------------------
## Test whether the con_bls. UCC only contains unique items in terms of UCC.
## It does not. 
## Match UCCs reported more than once to their expenditure class if that 
## is the same. Some UCCS also matched to different exp. classes.
## Expenditure class is in price level hierarchie one step above item_stratum.
#------------------------------------------------------------------------

UCC_u =pd.DataFrame(data= con_bls.UCC.unique(), columns=['unique_UCCs'])

dups = con_bls[con_bls.UCC.duplicated(keep=False)] # keep= False marks all duplicates as True 
print('There are', len(UCC_u), 'unique UCCs in the concordance file, and', len(dups.UCC.unique()),\
      'are reported more then once.' )

#pd.DataFrame(dups[['item_id','UCC']].sort_values('UCC')).to_excel\
#('../../original_data/tb_printed/duplicates_UCC.xlsx')


con_bls['dupsII'] = con_bls.UCC.duplicated(keep=False)

reggae =re.compile('\d+')
con_bls['exp_class']=""
for i in range(0,len(con_bls)):
    if con_bls.dupsII.iloc[i]:
        con_bls['exp_class'].iloc[i]=reggae.split(con_bls['item_id'].iloc[i])[0]
    
con_bls['Bool']= con_bls.duplicated(['UCC', 'exp_class'], keep=False)     
 
for i in range(0,len(con_bls)):
    if con_bls.Bool.iloc[i]:
        con_bls['item_id'].iloc[i]=con_bls['exp_class'].iloc[i]

# drop duplicates
con_bls['dupIII']=con_bls.duplicated(['UCC', 'item_id'] )
con_bls=con_bls[~con_bls.dupIII]
con_bls.index=range(0,len(con_bls))

# for all remaining duplicates in terms of UCC only
con_bls['dupsIV']=con_bls.UCC.duplicated(keep=False)
# there are only 15 UCCs that have duplicates. 
# for now, pick one item stratum randomly.
con_bls=con_bls[~con_bls.UCC.duplicated()]
# Test for remaining duplicates in terms of UCC
con_bls['dupsV']=con_bls.UCC.duplicated(keep=False)
s = con_bls[['dupsV', 'UCC']][con_bls.dupsV]

assert len(s.UCC.unique())==0
print('There are', len(s.UCC.unique()), 'duplicates left in the concordance file.')

# cleaned concordance file
con_bls=con_bls[['item_id', 'UCC']]

con_bls.to_pickle('../../original_data/Concordance/BLS_con')
#------------------------------------------------------------------------
## Merge
#------------------------------------------------------------------------

# use outer merge to decide how to deal with non-merged UCCs
d_CPI_test=d_CPI.merge(con_bls, left_on= 'concordance_id', right_on= 'item_id', how= 'outer', validate='m:m' , indicator= 'source') 

#------------------------------------------------------------------------
## Check what concordance_id could not be merged.
#------------------------------------------------------------------------

not_merged_in_CPI=d_CPI_test[['concordance_id','source']]

not_merged_in_CPI=not_merged_in_CPI[not_merged_in_CPI.source=='left_only']
not_merged_in_CPI=not_merged_in_CPI.drop_duplicates('concordance_id')
s= not_merged_in_CPI.concordance_id.unique()

# 145 CPI series could not be merged. 
# the non-merged d_CPI items are either expenditure classes where we choose
# to merge the more granular item_stratum level. Or prices of ELIs that we 
# did not expect to have in the price data set. 

not_merged_in_CPI['item_stratum_non_merged']=""

not_merged_in_CPI.index=range(0,len(not_merged_in_CPI))
for i in range(0, len(not_merged_in_CPI)):
    if re.search('^\w{2}\d{2}$',not_merged_in_CPI['concordance_id'].iloc[i]):
        not_merged_in_CPI['item_stratum_non_merged'].iloc[i]=True
    else:
        not_merged_in_CPI['item_stratum_non_merged'].iloc[i]=False

not_merged_item_in_CPI=not_merged_in_CPI[not_merged_in_CPI.item_stratum_non_merged]

# 1 item stratum not merged: TB01. This stratum was coded as an expenditure class. 
# It was not able to differentate between TB01 and TB02 as they had the same UCCs
# in the concordance file. The uCC was therefore merged to the respective expendi-
# ture class.

#------------------------------------------------------------------------
## Check what CPIs from concordance file are not in CPI file
## match, if possible to respective expenditure class.
#------------------------------------------------------------------------
not_merged_in_con=d_CPI_test[['source', 'item_id_y','UCC']] #item_id_y is from con file

not_merged_in_con=not_merged_in_con[not_merged_in_con.source=='right_only']
# there are 151 non_merged UCCs, they can be matched to the expenditure class

# derive expenditure class
not_merged_in_con['item_id_new']=""
for i in range(0,len(not_merged_in_con)):
    not_merged_in_con['item_id_new'].iloc[i]=not_merged_in_con.item_id_y.iloc[i][:2]
  
con_exp_class=not_merged_in_con[['item_id_new', 'UCC']]
con_exp_class.columns=['item_id_II', 'UCC']

#update concordance file: replace item_id in BLS concordance by exp class id.
con_bls=con_bls.merge(con_exp_class, left_on='UCC', right_on='UCC', how = 'left', validate = "1:1")

for i in range(0,len(con_bls)):
    if pd.isna(con_bls.item_id_II.iloc[i])==False:
        con_bls.item_id.iloc[i]= con_bls.item_id_II.iloc[i]
con_bls= con_bls[['item_id', 'UCC']]

# only unique UCCs?
assert len(con_bls.UCC.duplicated().unique())==1
print('There are only unique UCCs in the con_bls file.')

#------------------------------------------------------------------------
## Final merge
## to item_id in con_bls (which is not unique) merge respective price info.
#------------------------------------------------------------------------

# only unique item-year-period combinations?
assert len(d_CPI.duplicated(['series_id', 'year','period']).unique())==1
print('There are only unique series_id-year-month combinations in the CPI file,\
ie. there is only one value per series/year/month combination.')

d_CPI_con=con_bls.merge(d_CPI, left_on= 'item_id', right_on= 'concordance_id', how= 'left',  validate="m:m") 

# check for uniqueness of UCC per year and period
d_CPI_con['dups']=d_CPI_con.duplicated(['UCC', 'year','period'], keep=False)
dups_in_con = d_CPI_con[d_CPI_con.dups].sort_values(['UCC', 'year', 'period'])

assert len(dups_in_con)==0
print('There are', len(dups_in_con), 'duplicates in terms of UCC year and period in the CPI data set.' )

#------------------------------------------------------------------------
## Clean CPI file to only contain prices that could be merged to 
## UCC codes.
#------------------------------------------------------------------------

d_CPI_con.UCC=d_CPI_con.UCC.astype(float)

#------------------------------------------------------------------------
## Aggregate price data on quarterly level using the mean of the 3 months
#------------------------------------------------------------------------

data_q= _quarter_collapse(d_CPI_con)
#------------------------------------------------------------------------
## save files
#------------------------------------------------------------------------

data_q.to_pickle('../../original_data/CPI_prepared/CPI_q')
d_CPI_con.to_pickle('../../original_data/CPI_prepared/CPI_m')