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
# series of codes that have negative expenditure values
# ------------------------------------------------------------------------
to_drop = pd.read_pickle("../out_data_mngment/codes_negatives/negatives_to_drop")
# ------------------------------------------------------------------------
## Read in data
# ------------------------------------------------------------------------

#base period
data_base = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi_01_1996")
data_base = data_base[['UCC', 'value']].drop_duplicates('UCC')
data_base.columns =['UCC', 'base_value']


for n, i in enumerate(listdir(
    "../out_data_mngment/CEX_merged_CPI/")):
    data_j_i = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/"+i)
    
    #---------------------------------------------------------------------
    # drop expenditure categories that have negative values in a ny period
    #---------------------------------------------------------------------    
    
    data_j_i=data_j_i[~data_j_i["CodeDescription"].isin(to_drop)]
    
    # ------------------------------------------------------------------------
    # Collapse data set on percentile level
    # ------------------------------------------------------------------------
    
    exp_data_j_i = data_j_i.groupby(
        ["Percentile", "UCC", "CodeDescription", "value"], as_index=False
    ).agg({"Weighted_exp": "sum"})
    
    # ------------------------------------------------------------------------
    # Merge base year index
    # ------------------------------------------------------------------------
    
    exp_data_j_i=exp_data_j_i.merge(data_base, left_on= 'UCC', right_on= 'UCC', validate = 'm:1', indicator ='source')
    
    #check for UCCs where we do not have CPI value of previous month
    print( len(exp_data_j_i['source'][exp_data_j_i['source']!='both']), 'UCCs today could not be merged to base period.\
    If !=0, Think about adjusting code!')
    
    # only keep matched values
    exp_data_j_i=exp_data_j_i[exp_data_j_i['source']=='both']
    
    
    # ------------------------------------------------------------------------
    # Rebase index
    # ------------------------------------------------------------------------
    
    exp_data_j_i['rebased_index'] = exp_data_j_i['value']/exp_data_j_i['base_value']
    
    # ------------------------------------------------------------------------
    # Deflate expenditures using rebased index for all item strata
    # and aggregate to total expenditures by percentile
    # ------------------------------------------------------------------------
    
    exp_data_j_i['real_exp_stratum']= exp_data_j_i['Weighted_exp']/exp_data_j_i['rebased_index']
    real_exp_j_i=exp_data_j_i.groupby(["Percentile"], as_index=False).agg(
            {"real_exp_stratum": "sum", "Weighted_exp": "sum"})
    
    real_exp_j_i.columns=['Percentile', 'real_exp', 'nominal_exp']
    
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
