""" This file is to 
    1) construct household percentiles of income distribution  
    2) calculate expenditure weights on percentile level

1) 
i)   Read in ITBI/ITII files. ITBI until 2004, startind from 2004 ITII, that's 
     when they are first available.
ii)  Merge sampling weights from FMLI file. 
-----Tests for how many Consumer Units (CUs) have not reported income ------
iii) Derive income distribution percentiles. 

"""
##############################################################################

import numpy as np
import pandas as pd
import os
import re

from functions import _cum_distribution
##############################################################################

""" i) and ii) Read in data. """

data = pd.read_csv('../../data/CEX_Data/intrvw96/itbi961x.csv')
 
weights=pd.read_csv('../../data/CEX_Data/intrvw96/fmli961x.csv')[['NEWID', 'FINLWT21']]
# Note to m,yself
# the data set weights only contains each CU once, thus, weights are the same for each quarter! Make sense as for each month within a quarter
# the sample is the same , test: 
# unique_weights =pd.unique(weights['NEWID'])
    
data=data.merge(weights, left_on= 'NEWID', right_on= 'NEWID', how= 'left')


""" Tests.

1) check whether all NEWID in data has been matched

 """

if len( data[data['NEWID'].isin(weights['NEWID'])].index)==len(data.index):
    print("Length of data matches. All CUs in data got a sampling weight.")
else:
    print("Error: There are CUs without weight.")
  
    
""" 2) check how many households will be missing due to no income reported."""

if len(pd.unique(data['NEWID']))==len(pd.unique(data[data['UCC']==980000]['NEWID'])):
    print('All households reported income')
else:
    s = len(pd.unique(data['NEWID']))-len(pd.unique(data[data['UCC']==980000]['NEWID']))
    print(s, ' households did not report income and will be missing.' )
   
#################################################################################
    
""" iii) Derive income distribution percentiles for pre-tax income. 
    
Derive percentiles for each month separately. This 
    
"""
 
# Note to myself: the UCC-item 'Income before taxes' and 'Income after taxes' don't 
# need to be divided by 4! a specified for other income variables in the ITBI/ITII files.
      
income_data_before_tax=data[data['UCC']==980000]
    
income_12_1995=income_data_before_tax[income_data_before_tax['REFMO']==12 ]

""" Test. 

Ensure there is only one year, i.e. all observations stem from the same month-year combination.

"""

class MyError(LookupError):
    '''to be looked up.'''


if len(pd.unique(income_12_1995['REFYR']))==1:
    print('test passed: only one year')
else:
   raise MyError('test failed: several years although there should only be one!')
  


d=income_12_1995

""" Derive cummulative distribution function. """

data_distribution = _cum_distribution(d)

"""CONTINUE """

def weighted_percentile(d):
    """ Calculate the percentile of each household.
     
    1) Sum up the weights assigned to each household in the sample. 
       This gives the total amount of households represented by the sample.
    2) Sort the data starting from the lowest income in ascending order. 
       Add up the weights starting from the lowest income.
       All households with cumulated weights share below the threshold (p/100) 
       fall within the given percentile. 
       If the weights share is above or equal to p/100 then check whether the probability 
    3) The code takes care of cases where several households have reported the same income.
       Then the weighst will be added to calculate the percentile.
       
    d is the data set

    """
    n= d['FINLWT21'].sum() 
    d_sorted= d.sort_values('VALUE', na_position= 'first') # this creates a copy! So changing d_sorted does not change d!!
    d_sorted['index_sorted']= range(len(d_sorted))
    d_sorted['Percentile']= ""
    d_sorted['Cum_weights']=""
    d_sorted['Percentage_below']=""

    start = 0           # variable 'start' so not to overwright those percentiles already assigned! 
    cum_weight=0.0
    
    for p in range(1, 5, 1):

        for i in range(start,len(d_sorted)+1):
        # first, while loop to assign correct weight, taking into account sum of weights of observations with the same value. 
                cum_weight_previous = cum_weight
                
                s = 0
                while d_sorted['VALUE'].iloc[i]==d_sorted['VALUE'].iloc[i+s]: 
                    
                    cum_weight += d_sorted['FINLWT21'].iloc[i+s]
                    s+=1 # s will thus have a value s.th. observation i+s is not yet included. 
                    
                d_sorted['Cum_weights'].iloc[i:i+s] = cum_weight # the end value is exlcuded! 
                d_sorted['Percentage_below'].iloc[i:i+s]= cum_weight/n
                
       # second, if-statement to check for the relevant percentile 
       # note that cum_weight gives the cummulative weight taking all equal observations into account
       
                if cum_weight/n < p/100 : # all observations with a value of which to observe equal or smaller values fall within the given percentile
                    d_sorted.loc[:,'Percentile'].iloc[i:i+s]=p
                                
                elif cum_weight/n >= p/100 and (1-cum_weight_previous/n)>=1-p/100: # at threshold, the second condition says that the 
                                                                                  # probability to observe an equal or higher income
                                                                                  # is >= 1-p/100. This is required since the data is 
                                                                                  # discrete. 
                    d_sorted.loc[:,'Percentile'].iloc[i:i+s]=p
                
                else: 
                    start = (i)   # since at the point of the break i+s is the index of the first observation that 
                                      # has not yet been assigned a percentile 
                                      # this is from where the operation has to start from for the next percentile.
        
                    cum_weight=d_sorted['Cum_weights'].iloc[(i-1)]      # the loop stops, ie. income of household i, has already been added
                                                                          # we have to ensure that the next loop starts from 
                                                                          # the previous cumulative value! Otherwise weight 
                                                                          # added twice!
                    break

        print('percentile', p, 'done!')
        
    return d_sorted[['NEWID','Cum_weights','FINLWT21','Percentile']]

"""NOW AS NEXT STEP HAVE TO THINK ABOUT HOW TO DEAL WITH EQUAL OBSERVATIONS: I think it DOES matter! :
    
either the ovbservation with a higher weight comes first, then threshold is passed. 
It will be assigned the next higher percentile. So will be the second observation. 
or the observation with a smaller weight, s.t. it fits the threshold comes first.
It will be assigned the lower threshold percentile. Only the second observation 
will be assigned the next higher percentile. 

QUESTION: does it make sense to have households with lower weights come first? I think so. 

Have to add up weights for equal observations and treat them as one! 
    
"""
 
    
    