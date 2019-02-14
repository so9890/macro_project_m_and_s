""" Local Projections estimation and impulse response functions plotting

"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

data = pd.read_pickle("../out_data_mngment/data_for_final_analysis/data_inequality")
data = data.sort_values(by=["year", "month"])
data.index = range(len(data))
stdev = data["sd"]
stdev.name = "stdev"


gini_coeff = data["Gini"]
gini_coeff.name = "gini_coeff"


p90_p10 = data["90-10"]
p90_p10.name = "p90_p10"


shock_series = pd.read_excel(
    "../original_data/Shocks_data/RR_MPshocks_Updated.xls", sheet_name="Sheet1"
)
shock_series = pd.concat(
    [data.loc[0:157]["year"], data.loc[0:157]["month"], shock_series], axis=1
)


b = pd.DataFrame(
    data=np.zeros((20, 3)), columns=["stdev", "gini_coeff", "p90_p10"]
)  # 20 lags

coeff_st_dev = pd.DataFrame(
    data=np.zeros((20, 3)), columns=["stdev", "gini_coeff", "p90_p10"]
)


for i, k in enumerate([stdev, gini_coeff, p90_p10]):
    x_1 = k.shift(1) - k.shift(2)
    x_1.name = "l_1"
    x_2 = k.shift(2) - k.shift(3)
    x_2.name = "l_2"
    X = pd.concat([x_1, x_2], axis=1)
    X["const"] = 1
    for h in range(20):
        y = k.shift(-h) - k.shift(-(h - 1))
        reg = sm.OLS(
            endog=y,
            exog=X[["const", "l_1", "l_2", "rr_l0", "rr_l1", "rr_l2"]],
            missing="drop",
        ).fit()
        b.loc[h, k.name] = reg.params[3]
        coeff_st_dev[h, k.name] = reg.bse[3]
