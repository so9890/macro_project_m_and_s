"""Calculate shares and real expenditures per percentile

"""
import pandas as pd
import numpy as np
from functions import gini
from os import listdir

# ------------------------------------------------------------------------
# DataFrame of inequality time series
# ------------------------------------------------------------------------

ineq_data = pd.DataFrame(data=np.zeros((len(listdir(
    "../out_data_mngment/CEX_merged_CPI/")), 5)), columns=["year","month","sd", "Gini", "90-10"])


# ------------------------------------------------------------------------
## Read in data
# ------------------------------------------------------------------------

for n, i in enumerate(listdir(
    "../out_data_mngment/CEX_merged_CPI/")):
    data_j_i = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/"+i)
    
#-------------------------------
# drop hh-s with negative income
#-------------------------------    
    data_j_i=data_j_i[data_j_i["Weighted_exp"].values>0]
# ------------------------------------------------------------------------
# Collapse data set on percentile level
# ------------------------------------------------------------------------

    exp_data_j_i = data_j_i.groupby(
        ["Percentile", "UCC", "CodeDescription", "value"], as_index=False
    ).agg({"Weighted_exp": "sum"})

# ------------------------------------------------------------------------
# Calculate total expenditure per percentile
# ------------------------------------------------------------------------

    exp_data_j_i_total = exp_data_j_i.groupby(["Percentile"], as_index=False).agg(
        {"Weighted_exp": "sum"}
    ) #nominal
    exp_data_j_i_total.columns = ["Percentile", "Total_expenditures"]

    exp_data_j_i = exp_data_j_i.merge(
        exp_data_j_i_total,
        left_on="Percentile",
        right_on="Percentile",
        how="left",
        validate="m:1",
        indicator="source",
    )

# ------------------------------------------------------------------------
# Calculate shares on UCC-Percentile level.
# ------------------------------------------------------------------------

    exp_data_j_i["share"] = pd.Series(
        data=exp_data_j_i["Weighted_exp"].values
        / exp_data_j_i["Total_expenditures"].values
    )

# keep relevant values
    exp_data_j_i = exp_data_j_i[
        ["Percentile", "UCC", "share", "Total_expenditures", "value", "CodeDescription"]
    ].sort_values(["Percentile", "UCC"])

    exp_data_j_i["percentile_cpi"] = (

        exp_data_j_i["share"] * exp_data_j_i["value"]
    )

# ------------------------------------------------------------------------
# Calculate percentile-specific price level and real consumption
# ------------------------------------------------------------------------
# sum up the share*values (percentile_cpi) by percentile value using group by
    real_exp_j_i = (
        exp_data_j_i.groupby("Percentile")[
            "percentile_cpi"].sum().reset_index()
    )
# retrieve nominal exp from exp_data
    real_exp_j_i["nominal_exp"] = (
        exp_data_j_i["Total_expenditures"]
        .drop_duplicates()
        .reset_index()["Total_expenditures"]
    )
# calculate real exp
    real_exp_j_i["real_exp"] = (
        real_exp_j_i["nominal_exp"] / real_exp_j_i["percentile_cpi"]
    )
# set percentile as index
    real_exp_j_i.index = real_exp_j_i["Percentile"]

# ----------------------------------
# Calculate inequality measures
# --------------------------------
    ineq_data.loc[n] = [
        i.split('_',3)[3],   
        i.split('_',3)[2],
        np.std(np.log(real_exp_j_i["real_exp"].values)),
        gini(real_exp_j_i["real_exp"].values),
        np.log(real_exp_j_i.loc[90]["real_exp"]) -
        np.log(real_exp_j_i.loc[10]["real_exp"]),
    ]


# ----------------
# Save data sets of real_exp
# ----------------
    real_exp_j_i.to_pickle("../out_data_mngment/data_for_final_analysis/cex_real_exp_"+i[7:])

# ----------------
# Save data sets of inequality measures
# ----------------
ineq_data.to_pickle("../out_data_mngment/data_for_final_analysis/data_inequality")
