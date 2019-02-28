"""Local Projections estimation and impulse response functions plotting."""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose


data = pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/data_inequality")
data = data.sort_values(by=["year", "month"])
data.index = range(len(data))
data["mm/yyyy"] = data["month"] + "/" + data["year"]
for c in data.columns[2:5]:
    plt.plot(data["mm/yyyy"], data[c])
    plt.ylabel(c)
    plt.xticks(data["mm/yyyy"][::8], rotation=70)
    plt.savefig("../out_figures/CPIU_agg_app/time_series_of" + c + "_with_agg_CPI-U", bbox_inches="tight")
    plt.clf()
#-------------------------
# reset index to dat_time
#------------------------
data['Date'] = pd.to_datetime(data['mm/yyyy'])
data = data.set_index('Date')

#---------------------------------------------------
# Construct series for estimation. Adjust seasonally
#---------------------------------------------------
stdev = data.iloc[:158]["sd"]
stdev.name = "stdev"
stdev = stdev - seasonal_decompose(stdev, model='additive').seasonal


gini_coeff = data.iloc[:158]["Gini"]
gini_coeff.name = "gini_coeff"
gini_coeff = gini_coeff - seasonal_decompose(gini_coeff, model='additive').seasonal


p90_p10 = data.iloc[:158]["90-10"]
p90_p10.name = "p90_p10"
p90_p10 = p90_p10 - seasonal_decompose(p90_p10, model='additive').seasonal



exp_10 = pd.read_pickle("../out_data_mngment/data_for_final_analysis/log_exp_series_p10")
exp_10 = exp_10.sort_values(by=["year", "month"])
exp_10 = exp_10.iloc[:158]["exp_p1-p10_het"]
exp_10.index = data.index[:158]
exp_10 = exp_10 - seasonal_decompose(exp_10, model='additive').seasonal



exp_90 = pd.read_pickle("../out_data_mngment/data_for_final_analysis/log_exp_series_p90")
exp_90 = exp_90.sort_values(by=["year", "month"])
exp_90 = exp_90.iloc[:158]["exp_p90-p100_het"]
exp_90.index = data.index[:158]
exp_90 = exp_90 - seasonal_decompose(exp_90, model='additive').seasonal

shock_series = (
    pd.read_excel(
        "../original_data/Shocks_data/RR_MPshocks_Updated.xls", sheet_name="Sheet1"
    )
    * 100
)
    
shock_series.index=data.index[:158]

shock_series = shock_series - seasonal_decompose(shock_series, model='additive').seasonal




# create data frame of regressors (don't changes with horizon h) for each ineq. measure

X = {}
for k in [stdev, gini_coeff, p90_p10, exp_10, exp_90]:
    X[k.name] = pd.DataFrame()
    X[k.name]["const"] = np.ones(len(shock_series))
    X[k.name].index = k.index
    for i in range(20):
        X[k.name]["rr_L" + str(i)] = shock_series["Shock_values"].shift(i)
    for j in range(1, 7):
        X[k.name]["dy_" + str(j)] = k.shift(j) - k.shift(j + 1)


# prepare dataframes for impulse responses and standard deviations
irf_values = pd.DataFrame()  # 20 lags

irf_st_dev = pd.DataFrame()

irf_pval = pd.DataFrame()

H = 20
for k in [stdev, gini_coeff, p90_p10, exp_10, exp_90]:
    for h in range(H + 1):
        y = k.shift(-h) - k.shift(-(h - 1))
        reg = sm.OLS(endog=y, exog=X[k.name], missing="drop").fit()
        rcov = reg.get_robustcov_results(
            cov_type="HAC", maxlags=10, use_correction=True
        )
        irf_values.loc[h, k.name] = rcov.params[1]
        irf_st_dev.loc[h, k.name] = rcov.bse[1]
        irf_pval.loc[h, k.name] = rcov.pvalues[1]
    plt.plot(irf_values[k.name], label="irf", color="black", linewidth=2)
    plt.plot(
        1.65 * irf_st_dev[k.name] + irf_values[k.name],
        "--",
        label="2_st_dev_up",
        color="grey",
    )
    plt.plot(
        -1.65 * irf_st_dev[k.name] + irf_values[k.name],
        "--",
        label="2_st_dev_down",
        color="grey",
    )
    x = np.arange(0, H + 1)
    plt.fill_between(
        x,
        1.65 * irf_st_dev[k.name] + irf_values[k.name],
        -1.65 * irf_st_dev[k.name] + irf_values[k.name],
        color="silver",
    )
    plt.plot([0] * (H + 1), color="red")
    plt.xlabel("time horizon")
    plt.ylabel(k.name)
    plt.savefig("../out_figures/CPIU_agg_app/" + k.name + "_with_agg_CPI-U", bbox_inches="tight")
    plt.clf()