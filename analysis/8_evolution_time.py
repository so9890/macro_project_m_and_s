"""
Plot real expenditures over time
"""
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
# read in data


for i in [10,90]:
    real_exp_i=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p"+ str(i))
    #real_exp_90=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")
    
    #sort data and save to one data frame
    df_sorted_i=real_exp_i.sort_values(['year', 'month'])
    
    df_sorted_i['time'] = df_sorted_i[['year', 'month']].apply(lambda x: '/'.join(x), axis=1)
    if i == 10:
        real_10=df_sorted_i
    else:
        real_90=df_sorted_i
    
        
# figure for poor
plt.plot(real_10['time'], real_10['exp_p1-p10_het'],'--', label="Poorest 10% ",color='orange',linewidth=2,scalex =False)
plt.plot( real_90['time'], real_90['exp_p90-p100_het'],'--', label="Richest 10%",color='blue')
plt.legend(loc=8)
plt.xticks(real_10['time'][::8],rotation=70)
plt.xlabel("Time")
plt.ylabel("Real Consumption")
plt.savefig("../out_figures/comparison_evolution/NEW_10_90_evolution",bbox_inches='tight')
plt.clf()

