"""
Plot real expenditures over time
"""
import pandas as pd
# read in data

real_exp_10_agg_cpi=pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p10")
real_exp_90_agg_cpi=pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p90")
real_exp_10=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p10")
real_exp_90=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")

data=[ 'real_exp_90_agg_cpi', 'real_exp_10', 'real_exp_90']

df_sorted=real_exp_10_agg_cpi.sort_values(['year', 'month'])
# sort data
for t in data:
    df_sorted=pd.merge(df_sorted, t, on = ['year', 'month'])

plt.plot(irf_values[k.name], label="irf",color='black',linewidth=2)
plt.plot(1.65 * irf_st_dev[k.name]+irf_values[k.name],'--', label="2_st_dev_up",color='grey')
plt.plot(-1.65 * irf_st_dev[k.name]+irf_values[k.name],'--', label="2_st_dev_down",color='grey')
x = np.arange(0,H+1)
plt.fill_between(x,1.65 * irf_st_dev[k.name]+irf_values[k.name],-1.65 * irf_st_dev[k.name]+irf_values[k.name],color='silver')
plt.plot([0]*H,color='red')
plt.xlabel("time horizon")
plt.ylabel(k.name)
plt.savefig("../out_figures/" + k.name,bbox_inches='tight')
plt.clf()


