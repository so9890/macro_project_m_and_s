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

 Read in ITBI/ITII files. Keep variables

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

data96q1 = pd.read_csv('../../data/CEX_Data/intrvw96/itbi961x.csv')

# filter out ucc values in the file to ensure the values added up are indeed income related
unique_UCC =pd.DataFrame(data=data96q1.T.loc['UCC']).drop_duplicates(subset='UCC')
#now merge info on UCC from CE_dictionary


helperI = pd.DataFrame(data=pd.read_excel('../CEX_Data_Documentation/CE_dictionary.xlsx', sheet_name=2).loc[:,'Variable Name':'Code Description'])

# only keep if Variable name == UCC, try outregular expressions later
UCC_Description = helperI.drop(helperI.loc[:,'Variable Name'][helperI.loc[:,'Variable Name']!=  'UCC'].index)

