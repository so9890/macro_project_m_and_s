# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
import re

""" Construct household level data on expenditures and weights of each category of
goods in the total expenditure

"""

#os.chdir('../data/CEX_Data')
#end_of_year = [

 #   '17']

#year_category = {
 #   'year': pd.Series(data=end_of_year),
  #  'expend_cat': pd.Series(data=os.listdir())
#}


""" First, derive percentile of households.

 Read in ITBI/ITII files. Keep following  variables

NEWID
REFMO
REFYR
Value note that value is given for several sources of income, they should be added up. 

Then need to merge sampling weight from FMLI file. Population percentile can 
differ from sample percentile! 

Then construct percentile indicator on year-month-CU level.  


Reference:
    working with zip files: https://www.geeksforgeeks.org/working-zip-files-python/

 """

data = pd.read_csv('../../data/CEX_Data/intrvw96/itbi961x.csv')

""" Add Sampling weight from respective fmli file. """
 
weights=pd.read_csv('../../data/CEX_Data/intrvw96/fmli961x.csv')[['NEWID', 'FINLWT21']]
# the data set weights only contains each CU once, thus, weights are the same for each quarter! Make sense as for each month within a quarter
# the sample is the same , test: 
#unique_weights =pd.unique(weights['NEWID'])
    
data=data.merge(weights, left_on= 'NEWID', right_on= 'NEWID', how= 'left')
# check whether all NEWID in data has been matched

if len( data[data['NEWID'].isin(weights['NEWID'])].index)==len(data.index):
    print("Length of data matches. All CUs in data got a sampling weight.")
else:
    print("Error: There are CUs without weight.")
# CHECK HOW TO RAISE EXCEPTIONS!!! 
    

""" Construct data frame that contains all UCC (in itbi files) and their description in the ITBI files """

# filter out ucc values in the file to ensure the values added up are indeed income related
#unique_UCC =pd.DataFrame(data=data['UCC']).drop_duplicates(subset='UCC')

#now merge info on UCC from CE_dictionary
helperI = pd.DataFrame(data=pd.read_excel('../CEX_Data_Documentation/CE_dictionary.xlsx', sheet_name=2).loc[:,'Survey':'Code Description'])


# there are only two survey types
#keep all INTERVIEW entries
helperI = helperI.drop(helperI.loc[:,'Survey'][~helperI.loc[:,'Survey'].str.contains('INTERVIEW')].index)

helperI= helperI.drop(helperI.loc[:,'File'][~helperI.loc[:,'File'].str.contains('(I|i)(T|t)(b|B)(I|i)')].index)
# note that ITBI imputed is only relevant for years 2004-2005! so drop for this analysis
helperI= helperI.drop(helperI.loc[:,'File'][helperI.loc[:,'File'].str.contains('m')].index)
# only keep if Variable name == UCC using a regular expression to make sure not losing any entry due to misspelling 
helperI = helperI.drop(helperI.loc[:,'Variable Name'][~helperI.loc[:,'Variable Name'].str.contains('(U|u)(c|C)(c|C)')].index)
# note there is only UCC now in the file
# and all Code Values are unique

# now only keep those observations in UCC_Description that are in data 
# the following dataframe contains all UCC that are in the data and their descriptions
# it can be used to check what items we add up as income
#unique_UCC_description=helperI[ np.isin(  helperI['Code Value'].astype(int).values, unique_UCC['UCC'].values)]
#print(unique_UCC_description['Code Description'])

""" Merge Code Description to data"""
# make Code Value in helperI an integer
helperI['Code Value'] = helperI['Code Value'].astype(int)
data=data.merge(helperI[['Code Value','Code Description']], left_on= 'UCC', right_on= 'Code Value', how= 'left')

""" There are strange UCCs in the income file. I wonder whether I can add them all up.... There is also the """
""" Can """

#match_NEWID= data[data['NEWID']==657965]
    
""" have to find out whether all households have a variable 'Income before tax' : No they don't, I sent an email to CE"""
    
#hh= pd.unique(data['NEWID'])
    
#income_pre_tax= data[data['UCC']==980000]
# check whether the number of unique households in this data set and in the full data set matches
#hh_income_pre_tax =  pd.unique(income_pre_tax['NEWID'])
# no it is not!!! there are 528 missing 
    
""" Derive percentile per month accounting for weights.

Note that the UCC-item 'Income before taxes' and 'Income after taxes' don't 
need to be divided by 4! a specified for other income variables in the ITBI/ITII files.

"""
       
#Only keep income before taxes and income after taxes as UCC, in separate data frames

income_data_before_tax=data[data['UCC']==980000]
income_data_after_tax=data[data['UCC']==980070]    

 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    