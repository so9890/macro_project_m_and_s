""" William Casey CPI_CE concordance. """

import pandas as pd
import re

# ------------------------------------------------------------------------
## Read in CPI and concordance file
# ------------------------------------------------------------------------
d_CPI = pd.read_pickle("../../original_data/CPI_prepared/CPI_for_con")
con = pd.read_excel(
    "../../original_data/Concordance/CPI_item_id_UCC_WilliamCassey_CPIRequirementsOfCE.xlsx",
    header=None,
    usecols="A:B",
    names=["concordance_sheet", "Drop"],
)

# page numbers in con.concordance_sheet have a nan in Drop!
con = pd.DataFrame(
    data=con.concordance_sheet[~pd.isna(con.Drop)], columns=["concordance_sheet"]
)
con.index = range(0, len(con))

# ------------------------------------------------------------------------
## Split column containing code into UCC and CPI item_id.
## Note that CPI codes are strings and UCCs are integers.
# ------------------------------------------------------------------------

con["UCC"] = ""
con["item_id"] = ""

for i in range(0, len(con)):
    if isinstance(con.concordance_sheet[i], int):
        con.UCC[i] = con.concordance_sheet[i]
    else:
        con.item_id[i] = con.concordance_sheet[i]

# only keep concordance

con = con[["concordance_sheet", "item_id", "UCC"]]

# ------------------------------------------------------------------------
## Merge item_id from CPI file. Only keep data that we have in the CPI
## file.
# ------------------------------------------------------------------------

# unique list of items in CPI file
c_CPI_unique = pd.DataFrame(
    data=d_CPI["concordance_id"].unique(), columns=["concordance_id"]
)
con = con.merge(
    c_CPI_unique,
    left_on="item_id",
    right_on="concordance_id",
    how="left",
    indicator="source",
    validate="m:1",
)  # many to one because of missing values

# ------------------------------------------------------------------------
# Whenever the variable source is left_only the item is an ELI.
# We only have Item stratum price level information.
# CAUTION: if all item_ids of a category get dropped by dropping nans,
# ie. >=2 nans after another, then the UCCs will be assigned to a wrong
# preceding item.
# ------------------------------------------------------------------------

# first, ensure that concordance_id is nan only for non_merged item_ids.
con.concordance_id[con.UCC != ""] = ""

con["BoolIII"] = ""
for i in range(0, len(con)):
    if pd.isna(con.concordance_id.iloc[i]):
        if pd.isna(con.concordance_id.iloc[i + 1]) | pd.isna(
            con.concordance_id.iloc[i - 1]
        ):
            con["BoolIII"][i] = True
        else:
            con["BoolIII"][i] = False
    else:
        con["BoolIII"][i] = ""

# ------------------------------------------------------------------------
# Drop those observations tfor which BOOLIII==False. They have no match in CPI
# file, are elis,. By dropping them the corresponding UCC will be assigned the
# item stratum id in the following.
# ------------------------------------------------------------------------

con = con[con.BoolIII != False]

# ------------------------------------------------------------------------
# in case BoolIII is True then the UCCs should be assigned to the next higher
# category of that we have CPI information. This ensures that all UCC in the
# concordance files will at least have a CPI counterpart. The next higher
# category is always given by two letters. Create a column with the first two
# letters of item_id. After all two letters there are numbers. Thw two letters
# give the 'Expenditure class'.
# ------------------------------------------------------------------------

# drop the second of the two following item_ids without match in CPI

con["BoolIV"] = ""
for i in range(0, len(con)):
    if con.BoolIII.iloc[i]:
        if con.BoolIII.iloc[i + 1]:
            con.BoolIV.iloc[i + 1] = True

con = con[con.BoolIV != True]

reggae = re.compile("\d+")
con.index = range(0, len(con))

for i in range(0, len(con)):
    if con.BoolIII.iloc[i] == True:
        con["item_id"].iloc[i] = con["item_id"].iloc[i][:2]
    else:
        con["item_id"].iloc[i] = con["item_id"].iloc[i]

# drop superfluous columns
con = con[["item_id", "UCC"]]

# ------------------------------------------------------------------------
## For concordance fill up empty cells in column item_id with previous entry.
## this will match item stratum and UCC codes.
# ------------------------------------------------------------------------

for i in range(0, len(con)):
    if re.search("(\w|\d)", con.item_id.iloc[i]):
        con.item_id.iloc[i] = con.item_id.iloc[i]
    else:
        con.item_id.iloc[i] = con.item_id.iloc[i - 1]

con = con[con.UCC != ""]
con.index = range(0, len(con))

# ------------------------------------------------------------------------
## Some item_ids are on ELI level. Since our price level is on Item-stratum level
## have to aggregate ELIs on item-stratum level: ie. first 4 digits of ELI
# ------------------------------------------------------------------------

con["item_id_new"] = ""
for i in range(0, len(con)):
    con["item_id_new"].iloc[i] = con.item_id.iloc[i][:4]

con = con[["item_id_new", "UCC"]]
con.columns = ["item_id", "UCC"]

# ------------------------------------------------------------------------
## Test whether the con.UCC only contains unique items.
## It does not. Thus, keep a list of duplicates and decide on where to
## match multiply named UCCs. This is important because consumers only
## spent their amount once and not twice.
# ------------------------------------------------------------------------

UCC_u = pd.DataFrame(data=con.UCC.unique(), columns=["unique_UCCs"])

dups = con[con.UCC.duplicated(keep=False)]  # keep= False marks all duplicates as True
print(
    "There are",
    len(UCC_u) - 1,
    "unique UCCs in the concordance file, and",
    len(dups.UCC.unique()),
    "are reported more then once.",
)

pd.DataFrame(dups[["item_id", "UCC"]].sort_values("UCC")).to_excel(
    "../../original_data/tb_printed/duplicates_UCC_WC.xlsx"
)
# dupplicates in terms of item_id and UCC can be dropped. they exist because
# on ELI level they are not duplicates but as we cannot differentiate between
# them on item-stratum we can pick one.

# identify second and higher order duplicates and drop them. Keep first one.
con["dup"] = con.duplicated()
con = con[["item_id", "UCC"]][con.dup == False]
con.index = range(0, len(con))

# For those items where only the UCC is a duplicate. Match the UCC to the
# respective expenditure class.
# This is reasonable as the expenditure class price level is a weighted
# aggregate of the corresponding item-stratum price levels.

con["dupsII"] = con.UCC.duplicated(keep=False)

reggae = re.compile("\d+")

for i in range(0, len(con)):
    if con.dupsII.iloc[i]:
        con["item_id"].iloc[i] = reggae.split(con["item_id"].iloc[i])[0]

# drop duplicates in terms of item_id and UCC, keep first observation of each
# duplicate group.

con["dup"] = con[["item_id", "UCC"]].duplicated()
con = con[["item_id", "UCC"]][con.dupsII == False]

# verify there are no duplicates in terms of UCC in the concordance file.

assert len(con) == len(con.UCC.unique())
print(
    "There are no UCC duplicates in the WC-concordance file. All expenditures \
will be assigned a unique price level."
)

con.to_pickle("../../original_data/Concordance/WC_con")
