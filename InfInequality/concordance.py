""" CPI_CE concordance. """

import pandas as pd
import re
#------------------------------------------------------------------------
## Read in CPI and concordance file
#------------------------------------------------------------------------

d_CPI = pd.read_pickle('../../original_data/CPI_prepared/CPI_m')

# The following takes the first row as header although it's not. But prefarable
# since can be directly accessed and first row is not needed anyway.
con = pd.read_excel('../../original_data/Concordance/tb_printed_CPI_item_id_manual.xlsx' , sheet_name = 1, usecols = "A:B", names =['concordance_sheet','Drop'])

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

# the variable Identifier in c is "nan" whenever the item_id (CPI)
# is not in our data set. It is, this is an ELI and we only have 
# Item stratum price level information. 

con =con[~pd.isna(con.Identifier)] 
con.index= range(0,len(con))

#------------------------------------------------------------------------
## For concordance fill up empty cells in column item_id with previous entry. 
## this will match item stratum and UCC codes. 
#------------------------------------------------------------------------

    
for i in range(0,len(con)):
    if re.search('(\w|\d)',con.item_id.iloc[i]):
        con.item_id.iloc[i]=con.item_id.iloc[i]
    else:
        con.item_id.iloc[i]=con.item_id.iloc[i-1]

con = con[['item_id', 'UCC']][con.UCC!=""]

con.to_pickle('../../original_data/Concordance/concordance_final')


