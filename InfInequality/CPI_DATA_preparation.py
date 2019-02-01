""" Preparing CPI data """

import pandas as pd

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

data = pd.read_excel('../../data/CPI_Data/food_and_beverages.xlsx')

for i in file_names[1:]:  
    data_helper = pd.read_excel('../../data/CPI_Data/'+ str(i) +'.xlsx')
    ## ensure same column names
    data_helper.columns= data.columns
    data = pd.concat([data, data_helper], sort= False)
 
del data_helper

#------------------------------------------------------------------------
## Now apply correction for year variable which contains part of
## the series_id
#------------------------------------------------------------------------

additional_column =  (data.T.loc['year']).str.split(expand=True)
additional_column.columns=['suffix', 'year']
data.loc[:,'series_id'] = ( pd.Series(data.T.loc['series_id']).str.
                            cat(additional_column.T.loc['suffix'], sep='', na_rep=' '))

boolean_isnan = pd.isna(pd.Series(additional_column.T.loc['year']))
data.loc[:,'year'][boolean_isnan == False] = additional_column.loc[:,'year']

#------------------------------------------------------------------------
## Aggregate price data on quarterly level using the mean of the 3 months
#------------------------------------------------------------------------

# create variable for quarter
for j in range(0,10,3):
    for i in range(1+j,4+j,1):
        if i <10:
            data.loc[data['period'].str.contains('0'+str(i)), 'quarter'] = 1+j/3
        else:
            data.loc[data['period'].str.contains(str(i)), 'quarter'] = 1+j/3

# collapse dataset on series_id, year and quarter level
data_quarterly=data.groupby(['series_id', 'year', 'quarter'], as_index = False).agg({"value": 'mean'})

#------------------------------------------------------------------------
## read in series identifier data only if in series_id of current dataset
#------------------------------------------------------------------------

#series_id = pd.DataFrame(data=data['series_id']).drop_duplicates(subset='series_id')
# also check for unique years
#unique_years =pd.DataFrame(data=data['year']).drop_duplicates(subset='year')

#------------------------------------------------------------------------
## save files
#------------------------------------------------------------------------

data.to_pickle('../../data/CPI_quarterly/??')