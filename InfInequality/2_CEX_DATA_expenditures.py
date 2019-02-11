"""  2) Calculate expenditure weights on percentile level. 

    i)    Prepare expenditure files first, only keep one month-year combination.
    ii)   Merge income percentiles to expenditure file for given month-year. 
    iii)  Merge CPI data and drop non-merged expenditures.
    iv)   Apply sampling weights to expenditures
    v)    Calculate shares.
   

    d_percentiles is the data set that results from running file CEX_DATA_percentiles. 

 """
import pandas as pd

###############################################################################

# ------------------------------------------------------------------------
# Add UCC code description. (Mariam: moved here to make out of loop)
# ------------------------------------------------------------------------

CE_dic = pd.read_excel(
    "../CEX_Data_Documentation/CE_dictionary.xlsx", sheet_name=2, usecols="A:E"
)

CE_dic = CE_dic[CE_dic.File == "MTBI"]  # this is only in the Interview survey
CE_dic = CE_dic[CE_dic.VariableName == "UCC"]
CE_dic.CodeValue = CE_dic.CodeValue.astype(int)
CE_dic = CE_dic[["CodeValue", "CodeDescription"]]


# ------------------------------------------------------------------------
# Loading and merging data sets.
# ------------------------------------------------------------------------
# , '962', '963', '964', '971', '972', '973', '974', '981', '982', '983', '984',
list_year = ['971','971x','972','973','974','981x','982','983','984']
#'991', '992', '993', '994', '001', '002', '003', '004', '011', '012', '013', '014', '021',
#'022', '023', '024', '031', '032', '033', '034', '041', '042', '044', '051', '052', '053',
#'054', '061', '062', '063', '064'

data_dict_exp = {}

for i in list_year:
    data = pd.read_csv("../original_data/CEX_Data/mtbi"+i+".csv")
    for j in data["REF_MO"].unique():
        data_i = data[data["REF_MO"] == j]
        ii = str(data_i["REF_YR"].unique())[1:5]
        data_i = data_i[["NEWID", "UCC", "COST"]]
        data_i.index = range(len(data_i))
        data_dict_exp[str(j)+'_'+ii+'_'+i] = data_i
 
       
list_1=list(data_dict_exp.keys()) 
list_2=list(set([item[:-4] for item in list_1]))
for l,v in enumerate(list_2):
     if v.endswith('_')==True:
         list_2[l]=list_2[l][:-1]

for i in list_2:
    x=[ii for ii in list_1 if ii.startswith(i)]
    data_i=pd.concat([data_dict_exp[k] for k in x],ignore_index=True)        
    d_percentiles = pd.read_pickle(
            "../out_data_mngment/Percentiles/" + i)    
##############################################################################################################
# read in percentiles
        #d_percentiles = pd.read_pickle(
         #   "../out_data_mngment/Percentiles/" + str(j)+'_'+ii)

# merge percentiles to expenditure data
    data_i = data_i.merge(
            d_percentiles,
            left_on="NEWID",
            right_on="NEWID",
            how="left",
            validate="m:1",
            indicator="source",
        )
# drop households without a percentile
    data_i = data_i[["NEWID", "UCC", "COST", "FINLWT21", "Percentile"]][
            data_i["source"] == "both"
        ]

    data_i = data_i.merge(
            CE_dic, left_on="UCC", right_on="CodeValue", how="left", indicator="source"
        )

# only keep those expenditures with a description

    data_i = data_i[
            ["UCC", "COST", "FINLWT21", "Percentile", "CodeDescription"]
        ][data_i.source == "both"]

# calculate weighted expenditures

    data_i["Weighted_exp"] = data_i["COST"] * data_i["FINLWT21"]
    data_i[["UCC", "Percentile", "Weighted_exp", "CodeDescription"]].to_pickle(
            "../out_data_mngment/CEX_output/data_"+i)
