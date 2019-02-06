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
## Also save away a column of ids that can be used to merge to the concor-
## dance file.
#------------------------------------------------------------------------

unique_SID= pd.DataFrame(data=data.series_id.unique(), columns=['series_id'])
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
         
unique_SID=unique_SID[unique_SID.concordance_id!=""]     
 
data=data.merge(unique_SID, left_on= 'series_id', right_on= 'series_id', how= 'left')
# there is no missing item_id in the data, there are 393 item of which 
# some will be dropped as they are too broad categories. 

#------------------------------------------------------------------------
## Check for missing values in year variable: print.
#------------------------------------------------------------------------

print('Are there missing year values in the data set?', pd.isna(data.year).unique())

# print number of years
p = pd.DataFrame(data=data.year.unique(), columns=['year']).sort_values('year',
                na_position= 'first')

print('There are', len(p), 'different years in the price data set.')


#------------------------------------------------------------------------
## Only keep data for years from 1995/12 onwards. CEX data at the moment not 
## available for earlier years.  
#------------------------------------------------------------------------

data = data[data.year.astype(int).isin(range(1995,2018,1))]

#assert no duplicates
assert len(data.duplicated(['series_id', 'year', 'period']).unique())==1
print('Each observation in CPI data is unique in terms of series, year and period at this stage.')

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
print ('There are no duplicates in the NS_concordance file in terms of variable \'eli88\', which is the right_on key. ')

# merge
data=data.merge(NS_concordance, left_on='concordance_id', right_on='eli88', how='left')

# work with a list of unique concordance_id and merge afterwards to data to speed up.
data['dup']=data.duplicated(['concordance_id'])
# the above does not have missing values. All values without any duplicate will be coded as false
c_id=data[['item_id','concordance_id', 'eli88', 'eli98', 'Description', 'label']][~data.dup]

for i in range(0,len(c_id)):
    if pd.isna(c_id.eli88.iloc[i]):
        c_id['concordance_id'].iloc[i]=c_id['concordance_id'].iloc[i]
    else:
        c_id['concordance_id'].iloc[i]=c_id['eli98'].iloc[i]
        
data=data.merge(c_id[['item_id', 'concordance_id']], left_on='item_id', right_on='item_id', how='left')       
        
data=data[['series_id', 'year', 'period', 'value',
       'Description',  'concordance_id_y'
       ]]
data.columns= ['series_id', 'year', 'period', 'value',
       'Description',  'concordance_id'
       ]    

data.to_pickle('../../original_data/CPI_prepared/CPI_for_con')























