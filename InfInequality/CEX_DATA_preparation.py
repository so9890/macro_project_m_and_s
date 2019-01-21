# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os


"""
Construct household level data on expenditures and weights of each category of
goods in the total expenditure

"""

os.chdir('../data/CEX_Data')
end_of_year = [

    '17']

year_category = {
    'year': pd.Series(data=end_of_year),
    'expend_cat': pd.Series(data=os.listdir())
}

""" Reading in necessary zip files

Need to get income information by variable 'newid'. 
This information is given in the itib files 

working with zip files: https://www.geeksforgeeks.org/working-zip-files-python/

 """

