""" Local Projections estimation and impulse response functions plotting
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


data = pd.read_pickle("../out_data_mngment/data_for_final_analysis/data_inequality")
data = data.sort_values(by=["year", "month"])
data.index = range(len(data))
data['mm/yyyy'] = data['month']+'/'+data['year']

stdev = data.loc[:157]["sd"]
stdev.name = "stdev"
plt.plot(data.loc[:157]['mm/yyyy'],stdev)
plt.ylabel('st. dev')
plt.xticks(data.loc[:157]['mm/yyyy'][::8],rotation=70)
plt.savefig("../out_figures/real_ineq_stdev" ,bbox_inches='tight')
plt.clf()


gini_coeff = data.loc[:157]["Gini"]
gini_coeff.name = "gini_coeff"
plt.plot(data.loc[:157]['mm/yyyy'],gini_coeff)
plt.ylabel('Gini')
plt.xticks(data.loc[:157]['mm/yyyy'][::8],rotation=70)
plt.savefig("../out_figures/real_ineq_Gini" ,bbox_inches='tight')
plt.clf()


p90_p10 = data.loc[:157]["90-10"]
p90_p10.name = "p90_p10"
plt.plot(data.loc[:157]['mm/yyyy'],p90_p10)
plt.ylabel('p90-p10')
plt.xticks(data.loc[:157]['mm/yyyy'][::8],rotation=70)
plt.savefig("../out_figures/real_ineq_p90-p10" ,bbox_inches='tight')
plt.clf()


exp_10 = pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p10")
exp_10 = exp_10.sort_values(by=["year", "month"])
exp_10 = exp_10["exp_p1-p10"]
exp_10.index = range(len(exp_10))
exp_10 = exp_10[:158]


exp_90 = pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")
exp_90 = exp_90.sort_values(by=["year", "month"])
exp_90 = exp_90["exp_p90-p100"]
exp_90.index = range(len(exp_90))
exp_90 = exp_90[:158]


shock_series = (
    pd.read_excel(
        "../original_data/Shocks_data/RR_MPshocks_Updated.xls", sheet_name="Sheet1"
    )
    * 100
)


# shock_series = pd.concat(
#    [data.loc[0:157]["year"], data.loc[0:157]["month"], shock_series], axis=1
# )

# create data frame of regressors (don't changes with horizon h) for each ineq. measure

X = {}
for k in [stdev, gini_coeff, p90_p10, exp_10, exp_90]:
    X[k.name] = pd.DataFrame()
    X[k.name]["const"] = np.ones(len(shock_series))
    for i in range(20):
        X[k.name]["rr_L" + str(i)] = shock_series["Shock_values"].shift(i)
    for j in range(1, 7):
        X[k.name]["dy_" + str(j)] = k.shift(j) - k.shift(j + 1)


# prepare dataframes for impulse responses and standard deviations
irf_values = pd.DataFrame()  # 20 lags

irf_st_dev = pd.DataFrame()

irf_pval = pd.DataFrame()


H= 20
for k in [stdev, gini_coeff, p90_p10, exp_10, exp_90]:
    for h in range(H+1):
        y = k.shift(-h) - k.shift(-(h - 1))
        reg = sm.OLS(endog=y, exog=X[k.name], missing="drop").fit()
        irf_values.loc[h, k.name] = reg.params[1]
        irf_st_dev.loc[h, k.name] = reg.bse[1]
        irf_pval.loc[h, k.name] = reg.pvalues[1]
    plt.plot(irf_values[k.name], label="irf",color='black',linewidth=2)
    plt.plot(1.65 * irf_st_dev[k.name]+irf_values[k.name],'--', label="2_st_dev_up",color='grey')
    plt.plot(-1.65 * irf_st_dev[k.name]+irf_values[k.name],'--', label="2_st_dev_down",color='grey')
    x = np.arange(0,H+1)
    plt.fill_between(x,1.65 * irf_st_dev[k.name]+irf_values[k.name],-1.65 * irf_st_dev[k.name]+irf_values[k.name],color='silver')
    plt.plot([0]*(H+1),color='red')
    plt.xlabel("time horizon")
    plt.ylabel(k.name)
    plt.savefig("../out_figures/" + k.name,bbox_inches='tight')
    plt.clf()
