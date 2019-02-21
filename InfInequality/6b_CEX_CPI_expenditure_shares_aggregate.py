"""Calculate shares and real expenditures on aggregate level"""
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
# Collapse data set on percentile level. merge aggregate CPI to this later.
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
    exp_data_j_i_total.columns = ["Percentile", "nominal_exp"]

    exp_data_j_i = exp_data_j_i.merge(
        exp_data_j_i_total,
        left_on="Percentile",
        right_on="Percentile",
        how="left",
        validate="m:1",
    )

#############################################################################
# The following is no longer on percentile level in order to derive aggregate 
# CPI.
# ------------------------------------------------------------------------
# Calculate total expenditures per UCC
# ------------------------------------------------------------------------

    helper_j_i = data_j_i.groupby(
        [ "UCC", "CodeDescription", "value"], as_index=False
    ).agg({"Weighted_exp": "sum"})

# ------------------------------------------------------------------------
# Calculate total expenditure 
# ------------------------------------------------------------------------

    helper_j_i['Agg_expenditures'] = helper_j_i.Weighted_exp.sum() #nominal
    
# ------------------------------------------------------------------------
# Calculate shares of UCC expenditures
# ------------------------------------------------------------------------

    helper_j_i["share"] = pd.Series(
        data=helper_j_i["Weighted_exp"].values
        / helper_j_i["Agg_expenditures"].values
    )

##########################################################################
# Back to data set on percentile level
# ------------------------------------------------------------------------
# Calculate aggregate price level and save to exp_opercentile data frame
# ------------------------------------------------------------------------
    exp_data_j_i["aggregate_cpi"] = (

    helper_j_i["share"] * helper_j_i["value"]
    ).sum()

# ------------------------------------------------------------------------
# Calculate real expenditures by percentile using agg. CPI
# ------------------------------------------------------------------------

    exp_data_j_i["real_exp"] = (
        exp_data_j_i["nominal_exp"].values / exp_data_j_i["aggregate_cpi"]
    )
    
# ------------------------------------------------------------------------
# Collapse on percentile level
# ------------------------------------------------------------------------

    real_exp_j_i = exp_data_j_i[["Percentile", "aggregate_cpi", "nominal_exp", "real_exp"]].drop_duplicates("Percentile")

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


# --------------------------
# Save data sets of real_exp
# --------------------------
    real_exp_j_i.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/cex_agg_cpi_real_exp_"+i[7:])

# ----------------
# Save data sets of inequality measures
# ----------------
ineq_data.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/data_inequality_agg_cpi")

#--------------------------------------------------------------------
# Construct series of real consumptions for 10th and 90th percentiles
#--------------------------------------------------------------------

real_exp_90=pd.DataFrame(columns=['year','month','exp_p90-p100'])
real_exp_10=pd.DataFrame(columns=['year','month','exp_p1-p10'])

for n,i in enumerate(listdir("../out_data_mngment/data_for_final_analysis_agg_cpi/")[:-1]):
       df= pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/"+i)
       real_exp_10.loc[n]=[
       i.split('__')[1].split('_')[1],
       i.split('__')[1].split('_')[0],
       np.mean(np.log(df["real_exp"][df["Percentile"]<=10]))
       ]
       real_exp_90.loc[n]=[
       i.split('__')[1].split('_')[1],
       i.split('__')[1].split('_')[0],
       np.mean(np.log(df["real_exp"][df["Percentile"]>=91]))
       ]
       
real_exp_10.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p10")
real_exp_90.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p90")

