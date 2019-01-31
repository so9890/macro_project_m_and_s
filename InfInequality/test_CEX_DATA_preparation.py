# -*- coding: utf-8 -*-
""" Test CEX_DATA_preparation.py """

import pandas as pd
import numpy as np
import pytest

from functions import _cum_distribution
from pandas.testing import assert_frame_equal, assert_series_equal

""" Test weighted_percentile.

This test asserts that the percentiles assigned to each household are correct. 

"""

# in the following fix starting values to be used as inputs in function 
@pytest.fixture
def setup_cum_distribution():
    """ This setup is to test if same values at the end are problematic. """
    out = {}
    out['d']  = pd.DataFrame(
        data=[[-10, 2, 3, 5, 3, -4,    7, 8.565565, 8.565565],
              [3.6, 5, 1, 3, 2,  1, 5.44,         4,       3]],
    index=  ['VALUE', 'FINLWT21']).T

    return out
setup = setup_cum_distribution()
n= setup['d']['FINLWT21'].sum()

@pytest.fixture
def expect_cum_distribution():
    """ This setup is to test if same values at the end are problematic. """
    out = {}
    values = [3.6, 4.6, 9.6, 12.6, 12.6, 15.6, 21.04, 28.04, 28.04]
    out['d']  = pd.DataFrame(
        data=[values,
              [x / values[-1] for x in values]
              ],
        index= ['Cum_weights', 'Percentage_below_equal']
        ).T
    
    return out
######################################################################

def test_cum_distribution(setup_cum_distribution, expect_cum_distribution):
    calc_distribution = _cum_distribution(**setup_cum_distribution())
    assert_frame_equal(calc_distribution['Cum_weights'], expect_cum_distribution()['d']['Cum_weights'])

######################################################################
""" The following is to debug the weighted_percentile function """

setup = setup_cum_distribution()
d=setup['d']
n= d['FINLWT21'].sum()
d_sorted= d.sort_values('VALUE', na_position= 'first')
d_sorted['index_sorted']= range(len(d_sorted))
d_sorted['Cum_weights']=""
d_sorted['Percentage_below_equal']=""
    
cum_weight=0.0   
s=0
number_skipped=0
for i in range(0,len(d_sorted)): 
        # if-statement to skip those observations that have 
        # had the same value as the previous one.
        if s== 0 and i==0: 
            number_skipped = 0
        else:
            number_skipped +=s-1
        j= i+number_skipped

        # This is the actual loop.
        # cum_weight_previous = cum_weight 
        s = 0
        while  d_sorted['VALUE'].iloc[j]==d_sorted['VALUE'].iloc[j+s]: 
             
             cum_weight += d_sorted['FINLWT21'].iloc[j+s]
             s+=1 
             
             if j+s==len(d_sorted): # if so, the next value to be tested would be out of range.
                 break
             else:
                 continue
            
        d_sorted['Cum_weights'].iloc[j:j+s] = cum_weight # the end value is exlcuded! 
        d_sorted['Percentage_below_equal'].iloc[j:j+s]= cum_weight/n

        if j+s == len(d_sorted):
            break
        else:
            continue

       
###################################################################################################    
@pytest.fixture
def expected_weighted_percentile():
    
    out = {}
    out['d'] = pd.DataFrame(
        data=[[-10, 0, 1, 2, 3, 4], [15, 15, 5, 30, 25, 10], [1, 2, ]]
        columns={'VALUE','FINLWT21','Percentile'},
    )
    
    return out



""" Test function for several equal values in loop """

@pytest.fixture
def setup_same_values():

    out = {}
    out['d'] = pd.DataFrame(
        data=[[2, 3, 2, 3, 3, -4], [3, 5, 1, 3, 2, 1]]).T
    out['d'].columns= {'VALUE','FINLWT21'}

    return out



s = 0
while d_sorted['VALUE'].iloc[i]==d_sorted['VALUE'].iloc[i+s]: 
    
    cum_weight += d_sorted['FINLWT21'].iloc[i+s]
    s+=1 # s will thus have a value s.th. observation i+s is not yet included. 
    
d_sorted['Cum_weights'].iloc[i:i+s] = cum_weight # the end value is exlcuded! 
d_sorted['Percentage_below'].iloc[i:i+s]= cum_weight/n


