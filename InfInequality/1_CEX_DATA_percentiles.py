""" This file is to 
    1) construct household percentiles of income distribution  
 
    i)   Read in ITBI/ITII files. ITBI until 2004, startind from 2004 ITII, that's 
         when they are first available.
    ii)  Merge sampling weights from FMLI file. 
    -----Tests for how many Consumer Units (CUs) have not reported income ------
    iii) Derive income distribution percentiles. 

"""
##############################################################################

import pandas as pd
import numpy as np

from functions import weights_percentiles

##############################################################################

""" i) and ii) Read in data. """
list_year = ['961']#, '962', '963', '964', '971', '972', '973', '974', '981', '982', '983', '984', 
             #'991', '992', '993', '994', '001', '002', '003', '004', '011', '012', '013', '014', '021',
             #'022', '023', '024', '031', '032', '033', '034', '041', '042', '044', '051', '052', '053', 
             #'054', '061', '062', '063', '064']
#data = {}
#weights={}

class MyError(LookupError):
    """to be looked up."""


for i in list_year:
    data =  pd.read_csv('../original_data/CEX_Data/itbi'+i+'.csv')
#data = pd.read_csv("../original_data/CEX_Data/itbi961x.csv")
    weights = pd.read_csv(
    "../original_data/CEX_Data/fmli"+i+".csv")[["NEWID", "FINLWT21"]]
    data = data.merge(weights, left_on="NEWID", right_on="NEWID", how="left")


    """ Tests.

    1) check whether all NEWID in data has been matched

    """


    if len(data[data["NEWID"].isin(weights["NEWID"])].index) == len(data.index):
        print("Length of data matches. All CUs in data got a sampling weight.")
    else:
        print("Error: There are CUs without weight.")


    """ 2) check how many households will be missing due to no income reported."""

    if len(pd.unique(data["NEWID"])) == len(
        pd.unique(data[data["UCC"] == 980000]["NEWID"])
    ):
        print("All households reported income")
    else:
        s = len(pd.unique(data["NEWID"])) - len(
        pd.unique(data[data["UCC"] == 980000]["NEWID"])
    )
        print(s, " households did not report income and will be missing.")

#################################################################################

    """ iii) Derive income distribution percentiles for pre-tax income. 
    
    Derive percentiles for each month separately. This 
    
    """

# Note to myself: the UCC-item 'Income before taxes' and 'Income after taxes' don't
# need to be divided by 4! a specified for other income variables in the ITBI/ITII files.

    income_data_before_tax = data[data["UCC"] == 980000]
    for j in income_data_before_tax["REFMO"].unique():
        income_j_i = income_data_before_tax[income_data_before_tax["REFMO"] == j]
        #this keeps those rows that correspond to month j.which is unique

        """ Test. 

        Ensure there is only one year, i.e. all observations stem from the same month-year combination.

        """



        if len(pd.unique(income_j_i["REFYR"])) == 1:
            print("test passed: only one year")
            dd = str(np.unique(income_j_i["REFYR"]))[1:5]
            #retrieves ref year if j=12
        else:
           raise MyError(
         "test failed: several years although there should only be one!")


        """ Derive cummulative distribution function and percentiles. """

        d = income_j_i
        d_percentiles = weights_percentiles(d)
        d_percentiles_j_i = d_percentiles[["NEWID", "FINLWT21", "Percentile"]]

        """ Save files. """
        d_percentiles_j_i.to_pickle("../out_data_mngment/Percentiles/"+str(j)+"_"+dd)
