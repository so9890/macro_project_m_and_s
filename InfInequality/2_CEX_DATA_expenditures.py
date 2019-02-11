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
list_year = ['961']
#'991', '992', '993', '994', '001', '002', '003', '004', '011', '012', '013', '014', '021',
#'022', '023', '024', '031', '032', '033', '034', '041', '042', '044', '051', '052', '053',
#'054', '061', '062', '063', '064'
for i in list_year:
    data = pd.read_csv("../original_data/CEX_Data/mtbi"+i+".csv")
    for j in data["REF_MO"].unique():
        data_j_i = data[data["REF_MO"] == j]
        ii = str(data_j_i["REF_YR"].unique())[1:5]
        data_j_i = data_j_i[["NEWID", "UCC", "COST"]]
        data_j_i.index = range(len(data_j_i))
##############################################################################################################
# read in percentiles
        d_percentiles = pd.read_pickle(
            "../out_data_mngment/Percentiles/" + str(j)+'_'+ii)

# merge percentiles to expenditure data
        data_j_i = data_j_i.merge(
            d_percentiles,
            left_on="NEWID",
            right_on="NEWID",
            how="left",
            validate="m:1",
            indicator="source",
        )
# drop households without a percentile
        data_j_i = data_j_i[["NEWID", "UCC", "COST", "FINLWT21", "Percentile"]][
            data_j_i["source"] == "both"
        ]

        data_j_i = data_j_i.merge(
            CE_dic, left_on="UCC", right_on="CodeValue", how="left", indicator="source"
        )

# only keep those expenditures with a description

        data_ = data_j_i[
            ["UCC", "COST", "FINLWT21", "Percentile", "CodeDescription"]
        ][data_j_i.source == "both"]

# calculate weighted expenditures

        data_j_i["Weighted_exp"] = data_j_i["COST"] * data_j_i["FINLWT21"]
        data_j_i[["UCC", "Percentile", "Weighted_exp", "CodeDescription"]].to_pickle(
            "../out_data_mngment/CEX_output/data_"+str(j)+"_"+ii
        )
