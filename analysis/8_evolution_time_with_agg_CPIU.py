"""
Plot real expenditures over time
"""
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
# read in data


for i in [10,90]:
    real_exp_i=pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/exp_series_p"+ str(i))
    #real_exp_90=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")
    
    #sort data and save to one data frame
    df_sorted_i=real_exp_i.sort_values(['year', 'month'])
    
    df_sorted_i['time'] = df_sorted_i[['year', 'month']].apply(lambda x: '/'.join(x), axis=1)
    if i == 10:
        real_10=df_sorted_i
    else:
        real_90=df_sorted_i
    
df_sorted_i.index = range(len(df_sorted_i))
# figure for poor
plt.plot(real_10['time'][1:-1], real_10['exp_p1-p10_het'][1:-1], label="Poorest 10% ",color='orange',linewidth=2, scalex =False)
plt.plot( real_90['time'][1:-1], real_90['exp_p90-p100_het'][1:-1], label="Richest 10%",color='blue')
plt.legend(loc=2)
plt.xticks(real_10['time'][1:-1][::8],rotation=70)
plt.xlabel("Time")
plt.ylabel("Well being")
plt.savefig("../out_figures/comparison_evolution/NEW_10_90_evolution_with_agg_CPI",bbox_inches='tight')
plt.clf()

