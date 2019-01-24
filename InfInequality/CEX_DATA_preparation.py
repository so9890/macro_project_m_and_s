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
    
""" Test how many households will be missing due to no income reported."""

if len(pd.unique(data['NEWID']))==len(pd.unique(data[data['UCC']==980000]['NEWID'])):
    print('All households reported income')
else:
    s = len(pd.unique(data['NEWID']))-len(pd.unique(data[data['UCC']==980000]['NEWID']))
    print(s, ' households did not report income and will be missing.' )
 

""" Derive percentile per month accounting for weights.

Note that the UCC-item 'Income before taxes' and 'Income after taxes' don't 
need to be divided by 4! a specified for other income variables in the ITBI/ITII files.

"""
       
income_data_before_tax=data[data['UCC']==980000]
#income_data_after_tax=data[data['UCC']==980070]    

"""1) only keep entries of one given month, later to be included in a loop"""
    
income_12_1995=income_data_before_tax[income_data_before_tax['REFMO']==12 ]
# ensure there is only one year! 
if len(pd.unique(income_12_1995['REFYR']))==1:
    print('test passed: only one year')
else:
    print('test failed: several years although there should only be one!')
    
"""  2) calculate income percentiles.
    
    I follow http://yiqun-dai.blogspot.com/2017/03/weighted-percentile-in-python-pandas.html

"""
d=income_12_1995


def weighted_percentile(d):
    """ Calculate the percentile of each household.
     
    1) Sum up the weights assigned to each household in the sample. 
       This gives the total amount of households represented by the sample.
    2) Multiply total amount of households represented by sample with the
       respective percentile to get the amount of households that are below
       a certain percentile.
    3) Sort the data starting from the lowest income in ascending order. 
       Add up the weights starting from the lowest income.
       All households with cumulated weights below the threshold fall within
       the given percentile. 
       
    d is the data set

    """
    
    d_sorted= d[:100].sort_values('VALUE', na_position= 'first') # this creates a copy! So changing d_sorted does not change d!!
    d_sorted['index_sorted']= range(len(d_sorted))
    d_sorted['Percentile']= ""
    d_sorted['Cum_weights']=""
    d_sorted['Percentage_below']=""
    n= d[:100]['FINLWT21'].sum() 
    start = 0           # variable 'start' so not to overwright those percentiles already assigned! 
    cum_weight=0.0
    
    for p in range(1, 50, 1):

        for i in range(start,len(d_sorted)):
   
            cum_weight += d_sorted['FINLWT21'].iloc[i]
            d_sorted['Cum_weights'].iloc[i]=cum_weight
            d_sorted['Percentage_below'].iloc[i]= cum_weight/n
            if cum_weight/n < p/100 :
                                     # note that the second condition from Kneip 
                                     # script is not needed as we work upwards from lowest values, 
                                     # and stop whenever the probability exceeds the percentile. 
                d_sorted.loc[:,'Percentile'].iloc[i]=p
                            
            elif cum_weight/n >= p/100 and (1-cum_weight/n+ d_sorted['FINLWT21'].iloc[i]/n)>=1-p/100: # at threshold
                
                d_sorted.loc[:,'Percentile'].iloc[i]=p
                
            else: 
                start = (i)   # since at the point of the break i is the index of the observation 
                                  # this is from where the operation has to start from for the next percentile.
    
                cum_weight=d_sorted['Cum_weights'].iloc[(i-1)]    # the loop stops, ie. i, has already been added to
                                                                      # we have to ensure that the next loop starts from 
                                                                      # the previous cumulative value! Otherwise weight 
                                                                      # added twice!
                break
#                else: 
 #                   print('smallest observation falls is treated wrongly')
                    
        print('percentile', p, 'done!')
        
    return d_sorted[['NEWID','Cum_weights','FINLWT21','Percentile']]

"""NOW AS NEXT STEP HAVE TO THINK ABOUT HOW TO DEAL WITH EQUAL OBSERVATIONS"""
# alternative    
#d_sorted['Cum_weights_alt']=""   
#for i in range(start,len(d_sorted)):
 #   d_sorted['Cum_weights_alt'].iloc[i]= d_sorted['FINLWT21'][:i+1].sum()
# works but also slow    
    
    