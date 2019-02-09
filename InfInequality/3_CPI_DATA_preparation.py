""" Preparing CPI data """

import pandas as pd
import re

#------------------------------------------------------------------------
## Create a list for the different excel files containing CI data
#------------------------------------------------------------------------

file_names =['food_and_beverages', 
             'USApparel', 
             'USCommoditiesServicesSpecial', 
             'USEducationandCommunication', 
             'UShousing', 
             'USMedical', 
             'USOtherGoodsAndServices', 
             'USRecreation', 
             'USTransportation'
             ]

#------------------------------------------------------------------------
## Merge Datasets
#------------------------------------------------------------------------

data = pd.read_table('../original_data/CPI_Data/food_and_beverages.txt')

for i in file_names[1:]:  
    data_helper = pd.read_table('../original_data/CPI_Data/'+ str(i) +'.txt')
    ## ensure same column names
    data_helper.columns= data.columns
    data = pd.concat([data, data_helper], sort= False)
 
del data_helper

#------------------------------------------------------------------------
## Apply correction for year variable which contains part of
## the series_id. 
## Ensure all columns have same type of entries. In variable year there are different types.
## That leads to errors when collapsing the data set.
## Mariam: No need for this since files are read from txt as tables
#------------------------------------------------------------------------3


#additional_column =  (data.year).str.split(expand=True)
#additional_column.columns=['suffix', 'year']
#data['series_id'] = ( pd.Series(data.series_id).str.
#                            cat(additional_column.suffix, sep='', na_rep=' '))

#boolean_isnan = pd.isna(pd.Series(additional_column.year))
#data.year[boolean_isnan == False] = additional_column.year

#------------------------------------------------------------------------
## Code variable year as int! Otherwise not recognised as equal years. 
## Ensure all other variables are also of one type.
#------------------------------------------------------------------------

data.year= data.year.astype(int)
data.series_id=data.series_id.astype(str)
data.value= data.value.astype(float)

#------------------------------------------------------------------------
## Only keep US city average prices, ie area_code==0000, 
## seasonal code (ie. 3rd letter)==U (not seasonally adjusted)
## periodicity code (ie. 4th letter)==R (monthly level)
#------------------------------------------------------------------------

#area-code
data=data[ data['series_id'].str.contains('0000')]

#seasonal-code
# keep a unique list of items to speed up.

unique_SID= pd.DataFrame(data=data.series_id.unique(), columns=['series_id'])

unique_SID['Bool_seasonal']=""
for i in range(0,len(unique_SID)):
    if unique_SID['series_id'].iloc[i][2]=='U':
        unique_SID['Bool_seasonal'].iloc[i] = True
    else:
        unique_SID['Bool_seasonal'].iloc[i] = False

unique_SID=unique_SID[unique_SID.Bool_seasonal]

#periodicity-code
unique_SID['Bool_period']=""
for i in range(0,len(unique_SID)):
    if unique_SID['series_id'].iloc[i][3]=='R':
        unique_SID['Bool_period'].iloc[i] = True
    else:
        unique_SID['Bool_period'].iloc[i] = False
        
unique_SID=unique_SID[unique_SID.Bool_period]   
 
#------------------------------------------------------------------------
## In the data files 'series_id' contains the item_code as the last part of the 
## string. Before the item code, there is the area code which consists of four 
## numbers and before it there are four letters. We ensured there is only
## the area code with '0000' in the data set.
## Also save away a column of ids that can be used to merge to the concor-
## dance file.
#------------------------------------------------------------------------

regexI= re.compile('[0]{4}')
unique_SID['item_id']= ""

regexIII =re.compile('^SE{1}?|^SS{1}?' )
unique_SID['concordance_id']=""

for i in range(0,len(unique_SID)):
    t=regexI.split(unique_SID['series_id'].iloc[i])
    unique_SID['item_id'].iloc[i]=t[1].strip()
    
    if len(regexIII.split(unique_SID['item_id'].iloc[i]))>1:
        unique_SID['concordance_id'].iloc[i]=regexIII.split(unique_SID['item_id'].iloc[i])[1]
    else:
         unique_SID['concordance_id'].iloc[i]=""
 
# drop item_id with SA, too broad categories. 
unique_SID=unique_SID[ unique_SID.concordance_id!=""]

#------------------------------------------------------------------------
## Column concordance_id contains only numerical values that refer to 
## identifiers used in 1988. The concordance_BLS file is based on 2015
## codes. Use cocnordance file from Nakamura-Steinsson that maps codes 
## from 1988 to those used in 2015.
#------------------------------------------------------------------------

# read in concordance file from Nakamura-Steinsson
NS_concordance = pd.read_excel('../../original_data/Concordance/ELIconcordance_NS.xls', sheet_name= 2, header=0, usecols="A:C")
NS_concordance['eli88']=NS_concordance.eli88.astype(str)

# note that 4 digit codes in concordance_id have a leading 0 but not in eli88. 
for i in range(0, len(NS_concordance)):
    if len(NS_concordance.eli88.iloc[i])==4:
        NS_concordance['eli88'].iloc[i]=str(0)+NS_concordance['eli88'].iloc[i]
        
assert len(NS_concordance.eli88.duplicated().unique())==1
NS_concordance['eli98_dups']=NS_concordance.eli98.duplicated() # only second or higher order duplicate are indicated as true
print ('There are no duplicates in the NS_concordance file in terms of variable\
\'eli88\', which is the right_on key. But there are', len(NS_concordance.eli98[NS_concordance.eli98.duplicated()].unique()) ,' in terms of \'eli98\'. Drop duplicates to avoid duplicates in final data set! ')

NS_concordance=NS_concordance[NS_concordance['eli98_dups']==False]

# merge to unique_SID file
unique_SID=unique_SID.merge(NS_concordance, left_on='concordance_id', right_on='eli88', how='left', validate= "1:1")


# replace concordance_id by eli98 if exists 
# the above does not have missing values. All values without any duplicate will be coded as false

for i in range(0,len(unique_SID)):
    if pd.isna(unique_SID.eli88.iloc[i]):
        unique_SID['concordance_id'].iloc[i]=unique_SID['concordance_id'].iloc[i]
    else:
        unique_SID['concordance_id'].iloc[i]=unique_SID['eli98'].iloc[i]

# test for duplicates
dups_con=unique_SID[unique_SID.concordance_id.duplicated(keep= False)].sort_values(['concordance_id', 'series_id'])
# there 21 duplicates in terms of eli98! drop duplicates in eli98 before merging to unique SID!

#------------------------------------------------------------------------
## merge back to main data set
#------------------------------------------------------------------------
        
data=data.merge(unique_SID[['series_id', 'item_id',
       'concordance_id']], left_on= 'series_id', right_on= 'series_id', how= 'left', validate="m:1")

# only keep items in price data set that have a concordance_id
data=data[~pd.isna(data.concordance_id)]

# check for duplicates in terms of concordance_id, year and period
dups=data.duplicated(['concordance_id', 'year', 'period'], keep=False)

assert len(dups.unique())==1
print('There are no duplicates in the final CPI file in terms of concordance_id, year and period.')

#------------------------------------------------------------------------
## Only keep data for years from 1995/12 onwards. CEX data at the moment not 
## available for earlier years.  
#------------------------------------------------------------------------

data = data[data.year.astype(int).isin(range(1995,2018,1))]

data.to_pickle('../../original_data/CPI_prepared/CPI_for_con')























