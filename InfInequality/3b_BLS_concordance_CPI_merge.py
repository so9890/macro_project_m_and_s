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


#save
con_bls.to_pickle('../../original_data/Concordance/BLS_con')
