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
from os import listdir

##############################################################################

""" i) and ii) Read in data. """
list_year_1 = [
    "961x",
    "962",
    "963",
    "964",
    "971x",
    "972",
    "973",
    "974",
    "981x",
    "982",
    "983",
    "984",
    "991x",
    "992",
    "993",
    "994",
    "001x",
    "002",
    "003",
    "004",
    "011x",
    "012",
    "013",
    "014",
    "021x",
    "022",
    "023",
    "024",
    "031x",
    "032",
    "033",
    "034",
]
list_year_2 = [
    "041x",
    "042",
    "043",
    "044",
    "051x",
    "052",
    "053",
    "054",
    "061x",
    "062",
    "063",
    "064",
    "071x",
    "072",
    "073",
    "074",
    "081x",
    "082",
    "083",
    "084",
    "091x",
    "092",
    "093",
    "094",
]
data_dict = {}
# weights={}


class MyError(LookupError):
    """to be looked up."""


for i in list_year_1:
    data = pd.read_csv("../original_data/CEX_Data/itbi" + i + ".csv")
    # data = pd.read_csv("../original_data/CEX_Data/itbi961x.csv")
    weights = pd.read_csv("../original_data/CEX_Data/fmli" + i + ".csv")[
        ["NEWID", "FINLWT21"]
    ]
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
        # this keeps those rows that correspond to month j.which is unique

        """ Test.

        Ensure there is only one year, i.e. all observations stem from the same month-year combination.

        """

        if len(pd.unique(income_j_i["REFYR"])) == 1:
            print("test passed: only one year")
            dd = str(np.unique(income_j_i["REFYR"]))[1:5]
            # retrieves ref year if j=12
        else:
            raise MyError(
                "test failed: several years although there should only be one!"
            )

        """ Derive cummulative distribution function and percentiles. """

        d = (
            income_j_i.groupby("NEWID", as_index=False)
            .apply(lambda x: x if len(x) == 1 else x.iloc[[-1]])
            .reset_index(level=0, drop=True)
        )
        # d_percentiles = weights_percentiles(d)
        # d_percentiles_j_i = d_percentiles[["NEWID", "FINLWT21", "Percentile"]]

        """ Save files. """
        data_dict[str(j) + "_" + dd + "_" + i[0:3]] = d

###############################################################################

for i in list_year_2:

    data = pd.read_csv("../original_data/CEX_Data/itii" + i + ".csv")
    # data = pd.read_csv("../original_data/CEX_Data/itbi961x.csv")
    weights = pd.read_csv("../original_data/CEX_Data/fmli" + i + ".csv")[
        ["NEWID", "FINLWT21"]
    ]
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
        # this keeps those rows that correspond to month j.which is unique

        """ Test.

        Ensure there is only one year, i.e. all observations stem from the same month-year combination.

        """

        if len(pd.unique(income_j_i["REFYR"])) == 1:
            print("test passed: only one year")
            dd = str(np.unique(income_j_i["REFYR"]))[1:5]
            # retrieves ref year if j=12
        else:
            raise MyError(
                "test failed: several years although there should only be one!"
            )

        d = income_j_i.groupby("NEWID").mean().reset_index()
        # d_percentiles = weights_percentiles(d)
        # d_percentiles_j_i = d_percentiles[["NEWID", "FINLWT21", "Percentile"]]

        data_dict[str(j) + "_" + dd + "_" + i[0:3]] = d

# for in listdir("../Income_month")
list_1 = list(data_dict.keys())
list_2 = list(set([item[:-4] for item in list_1]))
list_2 = sorted(list_2, key=lambda x: int(x[-4:]))
list_q_y = []
for q in range(1,5):
    for y in range(1995,2010):
        list_q_y.append(str(q)+'_'+str(y))

""" Derive cummulative distribution function and percentiles. """


for s, i in enumerate(list_2[9:]):
    x = [ii for ii in list_1 if ii.startswith(i)]
    data_i_j = pd.concat([data_dict[k] for k in x])
    d_percentiles = weights_percentiles(data_i_j)
    d_percentiles_i_j = d_percentiles[["NEWID", "FINLWT21", "Percentile"]]

    """ Save files. """

    d_percentiles_i_j.to_pickle("../out_data_mngment/Percentiles/" + i)
    print(len(list_2[9:]) - s - 1, "datasets left to generate")

for s, i in enumerate(list_q_y):
    q=range(int(i.split('_')[0])*3-2,int(i.split('_')[0])*3+1)
    y=int(i.split('_')[1])
    x=[ii for ii in list_1 if (int(ii.split('_')[0]) in q and int(ii.split('_')[1])==y)]
    data_q_y = pd.concat([data_dict[k] for k in x])
    data_q_y = data_q_y.groupby(["NEWID"]).sum() #what to do with te weights???
    d_percentiles = weights_percentiles(data_q_y)
    d_per_q_y=d_percentiles[["NEWID", "FINLWT21", "Percentile"]]
    d_per_qy.to_pickle("../out_data_mngment/Percentiles/" +"Q"+i)
    print(len(list_q_y) - s - 1, "datasets left to generate")

    
