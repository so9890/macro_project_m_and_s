from os import listdir
import pandas as pd
""" This file is to bring consumption shares and price data together. """

""" We have a file  with the expenditure shares on percentile-month/year-UCC level.
    And a file containing CPI data on monthly level. 
"""


# ------------------------------------------------------------------------
# Read in Data.
# ------------------------------------------------------------------------

d_CPI = pd.read_pickle("../out_data_mngment/CPI_prepared/CPI_m")

for i in listdir("../out_data_mngment/CEX_output/"):
    d_exp_j_i = pd.read_pickle("../out_data_mngment/CEX_output/"+i)

# ------------------------------------------------------------------------
# Keep Price information for respective month-year of expenditures.
# ------------------------------------------------------------------------

    d_CPI_j_i = d_CPI[d_CPI["year"] == int(i[-4:])]
    d_CPI_j_i = d_CPI_j_i[["series_id", "value", "UCC"]
                          ][d_CPI_j_i.period.str.contains(i.split("_", 3)[1])]

# ------------------------------------------------------------------------
# Merge CPI data set to expenditure data.
# ------------------------------------------------------------------------

# verify UCCs are integers in both files
    d_exp_j_i["UCC"] = d_exp_j_i["UCC"].astype(int)
    d_CPI_j_i["UCC"] = d_CPI_j_i["UCC"].astype(int)

    d_exp_j_i = d_exp_j_i.merge(
        d_CPI_j_i,
        left_on="UCC",
        right_on="UCC",
        how="left",
        validate="m:1",
        indicator="source",
    )

# ------------------------------------------------------------------------
# Use second concordance file from WS to match non-merged items.
# split merged expenditure file into merged and non_merged.
# ------------------------------------------------------------------------

    not_merged = d_exp_j_i[["Percentile", "UCC", "Weighted_exp", "CodeDescription"]][
        d_exp_j_i == "left_only"
    ]
    print(
        len(not_merged.drop_duplicates("UCC")),
        "UCCs could not be merged with BLS concordance.",
    )
# the reason is that those unmerged UCCs are not in the CPI file from 12_1995!

# also keep all merged UCCs that will be used to append data set later.
    merged = d_exp_j_i[
        ["Percentile", "UCC", "Weighted_exp",
            "CodeDescription", "series_id", "value"]
    ][d_exp_j_i.source == "both"]

# ------------------------------------------------------------------------
# Use the concordance file from William Casey to match so far unmatched UCCs.
# to derive this save a copy of the non_merged UCCs
# ------------------------------------------------------------------------

    d_CPI_WC = pd.read_pickle("../out_data_mngment/CPI_prepared/CPI_m_WC")

# keep relevant periods only
    d_CPI_WC_j_i = d_CPI_WC[d_CPI_WC["year"] == int(i[-4:])]
    d_CPI_WC_j_i = d_CPI_WC_j_i[["series_id", "value", "UCC"]][
        d_CPI_WC_j_i.period.str.contains(i[5:7])
    ]

# ensure UCC in d_CPI_WC is integer
    d_CPI_WC_j_i["UCC"] = d_CPI_WC_j_i["UCC"].astype(int)

    not_merged = not_merged.merge(
        d_CPI_WC_j_i,
        left_on="UCC",
        right_on="UCC",
        how="left",
        indicator="source",
        validate="m:1",
    )

# some items are still not merged.
    not_mergedII = not_merged[["UCC", "source"]]

    not_mergedII = not_mergedII[
        not_mergedII.source == "left_only"
    ]  # only keep those observations that are not in d_CPI_WC_12_1995

    print(
        len(not_mergedII.drop_duplicates("UCC")),
        "UCCs could not be merged after \
additional WS concordance. They are not in the CPI data set for the given month-year \
combination. Thus,",
        len(not_merged.drop_duplicates("UCC")) -
        len(not_mergedII.drop_duplicates("UCC")),
        "additinal observations merged thanks to WS concordance file.",
    )

# only keep observations that got merged
    mergedII = not_merged[
        ["Percentile", "UCC", "Weighted_exp",
            "CodeDescription", "series_id", "value"]
    ][not_merged.source == "both"]
# ------------------------------------------------------------------------
# Calculate EXPENDITURE SHARES from merged items.
# ------------------------------------------------------------------------

    exp_cpi_j_i = merged.append(mergedII)
    exp_cpi_j_i.to_pickle("../out_data_mngment/CEX_merged_CPI/exp_cpi"+i[4:])
