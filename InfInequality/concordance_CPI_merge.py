""" CPI_CE concordance. """

import pandas as pd
import re

from functions import _quarter_collapse

#------------------------------------------------------------------------
## Read in CPI and concordance file
#------------------------------------------------------------------------

d_CPI = pd.read_pickle('../../original_data/CPI_prepared/CPI_for_con')
con = pd.read_excel('../../original_data/Concordance/CPI_item_id_UCC_WilliamCassey_CPIRequirementsOfCE.xlsx' , header=None, usecols = "A:B", names =['concordance_sheet','Drop'])

# page numbers in con.concordance_sheet have a nan in Drop!
con=pd.DataFrame(data=con.concordance_sheet[~pd.isna(con.Drop)], columns= ['concordance_sheet'])
con.index = range(0,len(con))

#------------------------------------------------------------------------
## Split column containing code into UCC and CPI item_id.
## Note that CPI codes are strings and UCCs are integers. 
#------------------------------------------------------------------------

con['UCC'] = ""
con['item_id']=""

for i in range(0,len(con)):
    if isinstance(con.concordance_sheet[i], int):
        con.UCC[i]=con.concordance_sheet[i]
    else:
        con.item_id[i]= con.concordance_sheet[i]

# only keep concordance

con=con[['concordance_sheet','item_id','UCC']]

#------------------------------------------------------------------------
## Merge item_id from CPI file. Only keep data that we have in the CPI 
## file.
#------------------------------------------------------------------------

# unique list of items in CPI file
c_CPI_unique = pd.DataFrame(data=d_CPI['concordance_id'].unique(), columns=['concordance_id'])
c_CPI_unique['Identifier']="In CPI"
con=con.merge(c_CPI_unique, left_on= 'item_id', right_on= 'concordance_id', how= 'left')
con.Identifier[con.concordance_id=='']=""

#------------------------------------------------------------------------
# the variable Identifier in con is "nan" whenever the item_id (CPI)
# is not in our data set. It is, this is an ELI and we only have 
# Item stratum price level information. 
# CAUTION: if all item_ids of a category get dropped by dropping nans,
# ie. >=2 nans after another, then the UCCs will be assigned to a wrong 
# preceding item.
#------------------------------------------------------------------------

con['BoolIII']=""
for i in range(0,len(con)):
    if pd.isna(con.Identifier.iloc[i]):
        if pd.isna(con.Identifier.iloc[i+1])| pd.isna(con.Identifier.iloc[i-1]) :
            con['BoolIII'][i]=True
        else:
            con['BoolIII'][i]=False
    else:
        con['BoolIII'][i]=""

     
# in case BoolIII is True then the UCCs should be assigned to the next higher
# category of that we have CPI information. This ensures that all UCC in the 
# concordance files will at least have a CPI counterpart. The next higher 
# category is always given by two letters. Create a column with the first two 
# letters of item_id. After all two letters there are numbers. Thw two letters
# give the 'Expenditure class'.
        
# first, drop if Identifier == nan and BoolIII False, then the above explained
# issue does not apply. 
        
con=con[con['BoolIII']!=False]

# drop the second of the two following item_ids without match in CPI
con['BoolIV']=""
for i in range(0,len(con)):
    if con.BoolIII.iloc[i]:
        if con.BoolIII.iloc[i+1]:
            con.BoolIV.iloc[i+1]=True
            
con=con[con.BoolIV!=True]

# merge  the categories with no macth in CPI to their expenditure class.
reggae =re.compile('\d+')
con.index=range(0,len(con))

for i in range(0,len(con)):
    if con.BoolIII.iloc[i]==True:
        con['item_id'].iloc[i]=reggae.split(con['item_id'].iloc[i])[0]
    else:
        con['item_id'].iloc[i]=con['item_id'].iloc[i]
# drop superfluous columns
con=con[['item_id', 'UCC']]

#------------------------------------------------------------------------
## For concordance fill up empty cells in column item_id with previous entry. 
## this will match item stratum and UCC codes. 
#------------------------------------------------------------------------

    
for i in range(0,len(con)):
    if re.search('(\w|\d)',con.item_id.iloc[i]):
        con.item_id.iloc[i]=con.item_id.iloc[i]
    else:
        con.item_id.iloc[i]=con.item_id.iloc[i-1]

con = con[con.UCC!=""]
con.index=range(0,len(con))
con.to_pickle('../../original_data/Concordance/concordance_final')


#------------------------------------------------------------------------
## Test whether the con.UCC only contains unique items. 
## It does not. Thus, keep a list of duplicates and decide on where to 
## match multiply named UCCs. This is important because consumers only 
## spent their amount once and not twice.
#------------------------------------------------------------------------

UCC_u =pd.DataFrame(data= con.UCC.unique(), columns=['unique_UCCs'])

dups = con[con.UCC.duplicated(keep=False)] # keep= False marks all duplicates as True 
print('There are', len(UCC_u)-1, 'unique UCCs in the concordance file, and', len(dups.UCC.unique()) ,'are reported more then once.' )

pd.DataFrame(dups[['item_id','UCC']].sort_values('UCC')).to_excel('../../original_data/tb_printed/duplicates_UCC.xlsx')
# dupplicates in terms of item_id and UCC can be dropped. they exist because 
# on ELI level they are not duplicates but as we cannot differentiate between 
# them on item-stratum we can pick one.

# identify second and higher order duplicates and drop them. Keep first one. 
con['dup']=con.duplicated()
con=con[['item_id','UCC']][con.dup==False]
con.index=range(0,len(con))

# For those items where only the UCC is a cuplicate. Match the UCC to the 
# respective expenditure class.
# This is reasonable as the expenditure class price level is a weighted
# aggregate of the corresponding item-stratum price levels.

con['dupsII'] = con.UCC.duplicated(keep=False)

reggae =re.compile('\d+')

for i in range(0,len(con)):
    if con.dupsII.iloc[i]:
        con['item_id'].iloc[i]=reggae.split(con['item_id'].iloc[i])[0]
 
# drop duplicates in terms of item_id and UCC, keep first observation of each 
# duplicate group.

con['dup']=con[['item_id','UCC']].duplicated()
con=con[['item_id','UCC']][con.dupsII==False]

# verify there are no duplicates in terms of UCC in the concordance file.

assert len(con)==len(con.UCC.unique())
print ('There are no UCC duplicates in the concordance file. All expenditures \
will be assigned a unique price level.')


#------------------------------------------------------------------------
## Merge concordance file to CPI file. 
#------------------------------------------------------------------------

d_CPI=d_CPI.merge(con, left_on= 'concordance_id', right_on= 'item_id', how= 'left')
# check whether all observations in d_CPI could have been merged, 
# whether merge was correct
print('There are', len(d_CPI['UCC'][pd.isna(d_CPI['series_id'])]), 'unmerged CPI observations.' )

# check which prices could not be merged. Ensure these are broader categories only.
not_merged=d_CPI[['concordance_id','Description', 'item_id_y']]
not_merged=not_merged[pd.isna(not_merged.item_id_y)]
not_merged=not_merged.drop_duplicates('concordance_id')

not_merged['Boolean']=""
for i in range(0, len(not_merged)):
    if re.search('\d+',not_merged.concordance_id.iloc[i]):
        not_merged['Boolean'].iloc[i]=True
    else:
        not_merged['Boolean'].iloc[i]=False
not_merged=not_merged[not_merged.Boolean]
# 76 CPI codes of smaller categories were not listed in the concordance file.

#save
not_merged[['concordance_id','Description']].to_excel('../../original_data/tb_printed/not_merged_CPIs.xlsx')

#------------------------------------------------------------------------
## Clean CPI file to only contain prices that could have been merged to 
## UCC codes.
#------------------------------------------------------------------------

d_CPI = d_CPI[~pd.isna(d_CPI.item_id_y)]
d_CPI = d_CPI[['series_id', 'year', 'value', 'period', 'Description', 'concordance_id', 'UCC']]
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