""" Preparing CPI data """

import pandas as pd
import re
from functions import _quarter_collapse
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

data = pd.read_excel('../../original_data/CPI_Data/food_and_beverages.xlsx')

for i in file_names[1:]:  
    data_helper = pd.read_excel('../../original_data/CPI_Data/'+ str(i) +'.xlsx')
    ## ensure same column names
    data_helper.columns= data.columns
    data = pd.concat([data, data_helper], sort= False)
 
del data_helper

#------------------------------------------------------------------------
## Apply correction for year variable which contains part of
## the series_id. 
## Ensure all columns have same type of entries. In variable year there are different types.
## That leads to errors when collapsing the data set.
#------------------------------------------------------------------------

additional_column =  (data.year).str.split(expand=True)
additional_column.columns=['suffix', 'year']
data['series_id'] = ( pd.Series(data.series_id).str.
                            cat(additional_column.suffix, sep='', na_rep=' '))

boolean_isnan = pd.isna(pd.Series(additional_column.year))
data.year[boolean_isnan == False] = additional_column.year

#------------------------------------------------------------------------
## Code variable year as int! Otherwise not recognised as equal years. 
## Ensure all other variables are also of one type.
#------------------------------------------------------------------------

data.year= data.year.astype(int)
data.series_id=data.series_id.astype(str)
data.value= data.value.astype(float)

#------------------------------------------------------------------------
## Only keep US city average prices, ie area_code==0000
#------------------------------------------------------------------------

data=data[ data['series_id'].str.contains('0000')]

#------------------------------------------------------------------------
## In the data files 'series_id' contains the item_code as the last part of the 
## string. Before the item code, there is the area code which consists of four 
## numbers and before it there are four letters. We ensured there is only
## the area code with '0000' in the data set.
## Use a series of unique series_id and merge afterwards to speed it up.
#------------------------------------------------------------------------

unique_SID= pd.DataFrame(data=data.series_id.unique(), columns=['series_id'])
regexI= re.compile('[0]{4}')
unique_SID['item_id']= ""

for i in range(0,len(unique_SID)):
    t=regexI.split(unique_SID['series_id'].iloc[i])
    unique_SID['item_id'].iloc[i]=t[1].strip()


data=data.merge(unique_SID, left_on= 'series_id', right_on= 'series_id', how= 'left')

#------------------------------------------------------------------------
## Check for missing values in year variable:print.
#------------------------------------------------------------------------

print('Are there missing year values in the data set?', pd.isna(data.year).unique())

# print number of years
p = pd.DataFrame(data=data.year.unique(), columns=['year']).sort_values('year',
                na_position= 'first')

print('There are', len(p), 'different years in the price data set.')


###############################################################################

""" Derive Concordance with CEX data, ie. UCC. """
#------------------------------------------------------------------------
## Read in and clean series identifier, merge it to data sets.
#------------------------------------------------------------------------

series_id = pd.read_excel('../../original_data/CPI_Data/item_encoding_II.xlsx')
series_id.columns=['item_id', 'else_else']

# The second column contains first the item description followed by a number
# and additional things. Only filter the description before the first number. 

regex= re.compile('[0-9]+')
series_id['Description']=""

for i in range(0,len(series_id)):
    series_id['Description'].iloc[i]=regex.split(series_id.else_else.iloc[i])[0]

series_id = series_id[['item_id','Description']]

# Merge series_id item_code and data/data_q 'series_id' to check whether extraction worked. 

data=data.merge(series_id, left_on= 'item_id', right_on= 'item_id', how= 'left')


#------------------------------------------------------------------------
## Read in Nakamura-Steinson (NS) ELI Concordance file. 
#------------------------------------------------------------------------

concordance = pd.read_excel('../../original_data/ELIconcordance_NS_elusiveCostofInflation.xls', sheet_name=2, names= ['UCC','ELI_id', 'Description'], usecols= "A:C")


# The NS data set contains ELI_id. Since our price data is on item_stratum level
# we have to aggregate the identifier but keep the UCC code unchanged for now.
# The hierarchie in the CPI is such that the ELI_code consits of the item-stratum
# code as the four first digits and is then followed by additional identifiers.
# We thus have to filter out the first four digits.

concordance['item_id']=""
for i in range(0,len(concordance)):
    concordance['item_id'].iloc[i]=concordance.ELI_id.iloc[i][:4]


#------------------------------------------------------------------------
## Aggregate price data on quarterly level using the mean of the 3 months
#------------------------------------------------------------------------

data_q= _quarter_collapse(data)
#------------------------------------------------------------------------
## save files
#------------------------------------------------------------------------

data_q.to_pickle('../../data/CPI_prepared/CPI_q')
data.to_pickle('../../data/CPI_prepared/CPI_m')






