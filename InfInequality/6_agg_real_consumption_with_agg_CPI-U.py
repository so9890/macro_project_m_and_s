"""Calculate shares and real expenditures per percentile using agg CPI-U series. """
import pandas as pd
import numpy as np
from functions import gini
from os import listdir
import os
#-----------------------------------------------
# Clear directory before running the code anew
#-----------------------------------------------

folder = "../out_data_mngment/data_for_final_analysis_agg_cpi/"
for the_file in os.listdir(folder):
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception as e:
        print(e)
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
#data_base = pd.read_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi_01_1996")
#data_base = data_base[['UCC', 'value']].drop_duplicates('UCC')
#data_base.columns =['UCC', 'base_value']
CPI_series = pd.read_csv("../original_data/CPI_Data/CPI_agg_series.csv")[["Year","Period","Value"]]
for i in range(len(CPI_series)):
    CPI_series.at[i,"Period"] = str(CPI_series.at[i,"Period"][1:])+'_'+str(CPI_series.at[i,"Year"])
    CPI_series.at[i,"Value"] =  CPI_series.at[i,"Value"] /  CPI_series.at[12,"Value"]
#CPI_series.loc[:]["Period"]=CPI_series.loc[:]["Period"][1:]
#CPI_series['mm/yyyy'] = CPI_series["Period"][1:]+CPI_series["Year"]


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
        ["Percentile"], as_index=False
    ).agg({"Weighted_exp": "sum"})
    
   
    exp_data_j_i['real_exp']=exp_data_j_i["Weighted_exp"]/CPI_series["Value"][CPI_series["Period"]==i[8:]].values
    
    # ----------------------------------
    # Calculate inequality measures
    # --------------------------------
    ineq_data.loc[n] = [
        i.split('_',3)[3],   
        i.split('_',3)[2],
        np.std(np.log(exp_data_j_i["real_exp"].values)),
        gini(exp_data_j_i["real_exp"].values),
        np.log(exp_data_j_i.loc[89]["real_exp"]) -
        np.log(exp_data_j_i.loc[9]["real_exp"]),
    ]
    
    # --------------------------
    # Save data sets of real_exp
    # --------------------------
    exp_data_j_i.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/cex_real_exp_"+i[7:])

# ----------------
# Save data sets of inequality measures
# ----------------
ineq_data.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/data_inequality")

#--------------------------------------------------------------------
# Construct series of real consumptions for 10th and 90th percentiles
#--------------------------------------------------------------------

## NOTE this code does not work if has run before!

real_exp_90=pd.DataFrame(columns=['year','month','exp_p90-p100_het'])
real_exp_10=pd.DataFrame(columns=['year','month','exp_p1-p10_het'])


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

       
real_exp_10.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/exp_series_p10")
real_exp_90.to_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/exp_series_p90")

