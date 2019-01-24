# -*- coding: utf-8 -*-
""" Test CEX_DATA_preparation.py """

import pandas as pd
import numpy as np
import pytest

from CEX_DATA_preparation import weighted_percentile


""" Test weighted_percentile.

This test asserts that the percentiles assigned to each household are correct. 

"""

# in the following fix starting values to be used as inputs in function 
@pytest.fixture
def setup_weighted_percentile():

    out = {}
    out['d'] = pd.DataFrame(
        data=[[-10.5, 0, 1, 5, 3, -4], [3.6, 5, 1, 3, 2, 1]]).T
    out['d'].columns= {'VALUE','FINLWT21'}

    return out

d_sorted_percentiles = weighted_percentile(**setup_weighted_percentile())


@pytest.fixture
def expected_weighted_percentile():
    
    out = {}
    out['d'] = pd.DataFrame(
        data=[[-10, 0, 1, 2, 3, 4], [15, 15, 5, 30, 25, 10], [1, 2, ]]
        columns={'VALUE','FINLWT21','Percentile'},
    )
    
    return out

