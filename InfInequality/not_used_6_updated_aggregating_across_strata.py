"""Calculate shares and real expenditures per percentile """
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

#base period
data_base = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi_01_1996")
data_base = data_base[['UCC', 'value']].drop_duplicates('UCC')
data_base.columns =['UCC', 'base_value']


data_j_i = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi_02_1996")
data_j_lag_i = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi_01_1996")

#prepare data set of lagged stratum level CPI, unique on UCC level
# to be merged to current data set
data_j_lag_i=data_j_lag_i[['UCC', 'value']].drop_duplicates('UCC')
data_j_lag_i.columns= ['UCC', 'value_lagged']
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
# Merge lagged CPI
# ------------------------------------------------------------------------

exp_data_j_i=exp_data_j_i.merge(data_j_lag_i, left_on= 'UCC', right_on= 'UCC', validate = 'm:1', indicator ='source')

#check for UCCs where we do not have CPI value of previous month
print( len(exp_data_j_i['source'][exp_data_j_i['source']!='both']), 'UCCs today could not be merged to previous month. Think about adjusting code!')

#only keep matched values
exp_data_j_i=exp_data_j_i[exp_data_j_i['source']=='both']

# ------------------------------------------------------------------------
# calculate percentile specific weights
# AW^p_beta,s=EXP^p_[beta,s]
# s = item stratum
# beta = t (reference period for the weights in our case one specific month)
# v = pivot month, prior to when beta was first used    
# ------------------------------------------------------------------------

exp_data_j_i['AW']=exp_data_j_i['Weighted_exp'] /exp_data_j_i['value']

# ------------------------------------------------------------------------
# calculate sum of weighted price changes 
# (under the assumption that weights did not change from one period to the next)
# sum(AW^p_beta,s*IX^s_[b^s,t])_s/sum(AW^p_beta,s*IX^s_[b^s,t-1])_s 
# s = item stratum
# beta = t (reference period for the weights in our case one specific month)
# v = pivot month, prior to when beta was first used    
# ------------------------------------------------------------------------

exp_data_j_i['numerator']=(exp_data_j_i['AW']*exp_data_j_i['value'])
exp_data_j_i['denominator']=(exp_data_j_i['AW']*exp_data_j_i['value_lagged'])

#sum up weightes price indices on percentile level
helper=exp_data_j_i.groupby(['Percentile'], as_index=False).agg({"numerator": "sum", "denominator": "sum"})

helper['IX_t_tlagged']=helper['numerator']/helper['denominator'] 

########################################################################
# in a next step those short run price changes have to e
# ------------------------------------------------------------------------
# Calculate total expenditure per percentile
# ------------------------------------------------------------------------

exp_data_j_i_total = exp_data_j_i.groupby(["Percentile"], as_index=False).agg(
    {"Weighted_exp": "sum"}
) #nominal
exp_data_j_i_total.columns = ["Percentile", "Total_expenditures"]

# ------------------------------------------------------------------------
# Merge total expenditures by percentile to UCC expenditures
# ------------------------------------------------------------------------

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


# --------------------------
# Save data sets of real_exp
# --------------------------
real_exp_j_i.to_pickle("../out_data_mngment/data_for_final_analysis/cex_real_exp_"+i[7:])

# ----------------
# Save data sets of inequality measures
# ----------------
ineq_data.to_pickle("../out_data_mngment/data_for_final_analysis/data_inequality")

#--------------------------------------------------------------------
# Construct series of real consumptions for 10th and 90th percentiles
#--------------------------------------------------------------------

## NOTE this code does not work if has run before!

real_exp_90=pd.DataFrame(columns=['year','month','exp_p90-p100_het'])
real_exp_10=pd.DataFrame(columns=['year','month','exp_p1-p10_het'])


for n,i in enumerate(listdir("../out_data_mngment/data_for_final_analysis/")[:-1]):
       df= pd.read_pickle("../out_data_mngment/data_for_final_analysis/"+i)
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

       
real_exp_10.to_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p10")
real_exp_90.to_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")
