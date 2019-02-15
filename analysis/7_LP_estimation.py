""" Local Projections estimation and impulse response functions plotting

"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

data = pd.read_pickle("../out_data_mngment/data_for_final_analysis/data_inequality")
data = data.sort_values(by=["year", "month"])
data.index = range(len(data))


stdev = data.loc[:157]["sd"]
stdev.name = "stdev"


gini_coeff = data.loc[:157]["Gini"]
gini_coeff.name = "gini_coeff"


p90_p10 = data.loc[:157]["90-10"]
p90_p10.name = "p90_p10"


shock_series = pd.read_excel(
    "../original_data/Shocks_data/RR_MPshocks_Updated.xls", sheet_name="Sheet1"
)

# shock_series = pd.concat(
#    [data.loc[0:157]["year"], data.loc[0:157]["month"], shock_series], axis=1
# )

# create data frame of regressors (don't changes with horizon h) for each ineq. measure

X = {}
for k in [stdev, gini_coeff, p90_p10]:
    X[k.name] = pd.DataFrame()
    X[k.name]["const"] = np.ones(len(shock_series))
    for i in range(21):
        X[k.name]["rr_L" + str(i)] = shock_series["Shock_values"].shift(i)
    for j in range(1, 3):
        X[k.name]["dy_" + str(j)] = stdev.shift(j) - stdev.shift(j + 1)


# prepare dataframes for impulse responses and standard deviations
b = pd.DataFrame(
    data=np.zeros((20, 3)), columns=["stdev", "gini_coeff", "p90_p10"]
)  # 20 lags

coeff_st_dev = pd.DataFrame(
    data=np.zeros((20, 3)), columns=["stdev", "gini_coeff", "p90_p10"]
)


for k in [stdev, gini_coeff, p90_p10]:
    for h in range(21):
        y = k.shift(-h) - k.shift(-(h - 1))
        reg = sm.OLS(endog=y, exog=X[k.name], missing="drop").fit()
        b.loc[h, k.name] = reg.params[3]
        coeff_st_dev[h, k.name] = reg.bse[3]
