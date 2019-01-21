# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
"""
Created on Fri Dec 21 00:28:38 2018

@author: admin
"""

"""
Construct household level data on expenditures and weights of each category of
goods in the total expenditure
"""

os.chdir('C:\\Users\\admin\\Documents\\BGSE3rdsem\\macro')
end_of_year = [
    '96',
    '97',
    '98',
    '99',
    '00',
    '01',
    '02',
    '03',
    '04',
    '05',
    '06',
    '07',
    '08',
    '09',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15',
    '16',
    '17']
year_category = {
    'year': pd.Series(data=end_of_year),
    'expend_cat': pd.Series(data=os.listdir())
}
