""" CPI_CE concordance. """

import pandas as pd
import re

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
## Test whether the con_bls.UCC only contains unique items in terms of UCC.
## It does not. 
## Match UCCs reported more than once to their expenditure class if that 
## is the same. Some UCCS also matched to different exp. classes.
## Expenditure class is in price level hierarchie one step above item_stratum.
#------------------------------------------------------------------------

UCC_u =pd.DataFrame(data= con_bls.UCC.unique(), columns=['unique_UCCs'])

dups = con_bls[con_bls.UCC.duplicated(keep=False)] # keep= False marks all duplicates as True 
print('There are', len(UCC_u), 'unique UCCs in the concordance file, and', len(dups.UCC.unique()),\
      'are reported more then once.' )

pd.DataFrame(dups[['item_id','UCC']].sort_values('UCC')).to_excel\
('../../original_data/tb_printed/duplicates_UCC.xlsx')


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
con_bls=con_bls[['UCC', 'UCC NAME',  'item_id']]

#------------------------------------------------------------------------
## Merge
#------------------------------------------------------------------------

d_CPI["DataFrame_ID_CPI"]="CPI"
con_bls["DataFrame_ID_con"]="Concordance"
# use outer merge to decide how to deal with non-merged UCCs
d_CPI_test=d_CPI.merge(con_bls, left_on= 'concordance_id', right_on= 'item_id', how= 'outer') 

#------------------------------------------------------------------------
## Check what concordance_id could not be merged.
#------------------------------------------------------------------------

not_merged_in_CPI=d_CPI_test[['concordance_id','DataFrame_ID_CPI','DataFrame_ID_con']]

not_merged_in_CPI=not_merged_in_CPI[pd.isna(not_merged_in_CPI.DataFrame_ID_con)]
not_merged_in_CPI=not_merged_in_CPI.drop_duplicates('concordance_id')

# 136 CPI series could not be merged. 
# the non-merged d_CPI items are either expenditure classes where we choose
# to merge the more granular item_stratum level. Or prices of ELIs that we 
# did not expect to have in the price data set. 

not_merged_in_CPI['item_stratum_non_merged']=""
# drop one nan in concordance
not_merged_in_CPI=not_merged_in_CPI[~pd.isna(not_merged_in_CPI['concordance_id'])]
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
#------------------------------------------------------------------------
not_merged_in_con=d_CPI_test[['DataFrame_ID_CPI','DataFrame_ID_con', 'item_id_y','UCC']] #item_id_y is from con file

not_merged_in_con=not_merged_in_con[pd.isna(not_merged_in_con.DataFrame_ID_CPI)]
# there are 40 non_merged UCCs, they can be matched to the expenditure category

not_merged_in_con['item_id_new']=""
for i in range(0,len(not_merged_in_con)):
    not_merged_in_con['item_id_new'].iloc[i]=not_merged_in_con.item_id_y.iloc[i][:2]
  
con_exp_class=not_merged_in_con[['item_id_new', 'UCC']]
con_exp_class.columns=['item_id_II', 'UCC']

#update con file
con_bls=con_bls.merge(con_exp_class, left_on='UCC', right_on='UCC', how = 'left')

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
## if would do it otherway around would have duplication of CPI observations.
#------------------------------------------------------------------------

d_CPI_con=con_bls.merge(d_CPI, left_on= 'item_id', right_on= 'concordance_id', how= 'left') 
# check for uniqueness
r=d_CPI_con.duplicated(['series_id', 'year','period'])
len(r.unique())
""" There are duplicates""" 
""" CONTINUE TMR"""
#------------------------------------------------------------------------
## Clean CPI file to only contain prices that could be merged to 
## UCC codes.
#------------------------------------------------------------------------

d_CPI = d_CPI[~pd.isna(d_CPI.item_id)]
d_CPI.UCC=d_CPI.UCC.astype(float)

#------------------------------------------------------------------------
## Aggregate price data on quarterly level using the mean of the 3 months
#------------------------------------------------------------------------

data_q= _quarter_collapse(d_CPI)
#------------------------------------------------------------------------
## save files
#------------------------------------------------------------------------

data_q.to_pickle('../../original_data/CPI_prepared/CPI_q')
d_CPI.to_pickle('../../original_data/CPI_prepared/CPI_m')