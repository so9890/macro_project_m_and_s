"""Calculate shares and real expenditures per percentile

"""
import pandas as pd
import numpy as np
from functions import gini

# ------------------------------------------------------------------------
## Read in data
# ------------------------------------------------------------------------


data_12_1995 = pd.read_pickle("../input_data/exp_cpi_12_1995")

# ------------------------------------------------------------------------
## Collapse data set on percentile level
# ------------------------------------------------------------------------

exp_data_12_1995 = data_12_1995.groupby(
    ["Percentile", "UCC", "CodeDescription", "value"], as_index=False
).agg({"Weighted_exp": "sum"})

# ------------------------------------------------------------------------
## Calculate total expenditure per percentile
# ------------------------------------------------------------------------

exp_data_12_1995_total = exp_data_12_1995.groupby(["Percentile"], as_index=False).agg(
    {"Weighted_exp": "sum"}
)
exp_data_12_1995_total.columns = ["Percentile", "Total_expenditures"]

exp_data_12_1995 = exp_data_12_1995.merge(
    exp_data_12_1995_total,
    left_on="Percentile",
    right_on="Percentile",
    how="left",
    validate="m:1",
    indicator="source",
)

# ------------------------------------------------------------------------
##  Calculate shares on UCC-Percentile level.
# ------------------------------------------------------------------------

exp_data_12_1995["share"] = pd.Series(
    data=exp_data_12_1995["Weighted_exp"].values
    / exp_data_12_1995["Total_expenditures"].values
)

# keep relevant values
exp_data_12_1995 = exp_data_12_1995[
    ["Percentile", "UCC", "share", "Total_expenditures", "value", "CodeDescription"]
].sort_values(["Percentile", "UCC"])
exp_data_12_1995["percentile_cpi"] = (
    exp_data_12_1995["share"] * exp_data_12_1995["value"]
)

# ------------------------------------------------------------------------
##  Calculate percentile-specific price level and real consumption
# ------------------------------------------------------------------------
real_exp_12_1995 = (
    exp_data_12_1995.groupby("Percentile")["percentile_cpi"].sum().reset_index()
)
real_exp_12_1995["nominal_exp"] = (
    exp_data_12_1995["Total_expenditures"]
    .drop_duplicates()
    .reset_index()["Total_expenditures"]
)
real_exp_12_1995["real_exp"] = (
    real_exp_12_1995["nominal_exp"] / real_exp_12_1995["percentile_cpi"]
)
real_exp_12_1995.index = real_exp_12_1995["Percentile"]

# ----------------------------------
## Calculate inequality measures
# --------------------------------
ineq_data = pd.DataFrame(data=np.zeros((264, 3)), columns=["sd", "Gini", "90-10"])
ineq_data.loc[0] = [
    np.std(real_exp_12_1995["real_exp"].values),
    gini(real_exp_12_1995["real_exp"].values),
    real_exp_12_1995.loc[90]["real_exp"] - real_exp_12_1995.loc[10]["real_exp"],
]


#----------------
## Save data
#----------------
real_exp_12_1995.to_pickle("../data_for_final_analysis/cex_cpi_real_exp_12_1995")