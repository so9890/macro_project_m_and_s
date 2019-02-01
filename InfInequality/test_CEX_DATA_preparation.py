# -*- coding: utf-8 -*-
""" Test CEX_DATA_preparation.py """

import pandas as pd
#import numpy as np
import pytest

from functions import _cum_distribution, weights_percentiles
#from pandas.testing import assert_frame_equal, assert_series_equal
from numpy.testing import assert_array_almost_equal, assert_array_equal

###############################################################################

""" Test function to derived cummulative distribution function.

    This test asserts that the weights and percentages assigned to 
    each household are correct. 

    """

# in the following fix starting values to be used as inputs in function 
@pytest.fixture
def setup_fun():

    out = {}
    out['d']  = pd.DataFrame(
        data=[[-10, -10, 2, 3, 5, 3, -4,    0,   1, 1, 1,  7, 8.565564, 8.565565, 8.565565, 8.565565],
              [  2, 3.6, 5, 1, 3, 2,  1, 5.4,   2, 2, 2,  2,        3,        4,        3,        4]],
    index=  ['VALUE', 'FINLWT21']).T

    return out


@pytest.fixture
def expect_fun():
    
    out = {}
    values = [5.6, 5.6, 6.6, 12.0, 18.0, 18.0, 18.0, 23.0, 26.0, 26.0, 29.0, 31.0, 34.0, 45.0, 45.0, 45.0]
    number_equal_obs = [5.6, 5.6, 1.0, 5.4, 6.0 , 6.0, 6.0, 5.0, 3.0, 3.0, 3.0, 2.0, 3.0, 11.0, 11.0, 11.0 ]
    out['d']  = pd.DataFrame(
        data=[values,
              [x / values[-1] for x in values],
              [x/ values[-1] for x in number_equal_obs],
              [ 1, 1, 0.875556, 0.853333, 0.733333,  0.733333, 0.733333, 0.6, 0.488889, 
               0.488889, 0.422222, 0.355556, 0.311111, 0.244444, 0.244444, 0.244444],
               [1,1, 13, 15, 27, 27, 27, 40, 52, 52, 58, 65, 69, 100, 100, 100]],
        index= ['Cum_weights', 'Percentage_below_equal', 'Percentage_equal', 'Percentage_equal_above', 'Percentile']
        ).T
    
    return out

######################################################################

def test_cum_distribution_weights(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(calc_distribution['Cum_weights'].values, expect_fun['d']['Cum_weights'].values)

def test_cum_distribution_percentage(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(calc_distribution['Percentage_below_equal'].values, expect_fun['d']['Percentage_below_equal'].values)

def test_cum_distribution_point(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(calc_distribution['Percentage_equal'].values, expect_fun['d']['Percentage_equal'].values)

def test_cum_distribution_equal_above(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_almost_equal(calc_distribution['Percentage_equal_above'].values, expect_fun['d']['Percentage_equal_above'].values)
    
######################################################################
    
""" Test function that assignes percentiles. 

    To do this, it is enough to test the cummulative function weights_percentiles
    since it only consists of two functions of which the first one is tested
    exhaustively above. 
    
    """ 

def test_weights_percentiles(setup_fun, expect_fun):
    calc_percentiles = weights_percentiles(**setup_fun)
    assert_array_equal(calc_percentiles['Percentile'].values, expect_fun['d']['Percentile'].values)    
    
    
