"""
Plot real expenditures over time
"""
import pandas as pd
import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
# read in data

real_exp_10_agg_cpi=pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p10")
real_exp_90_agg_cpi=pd.read_pickle("../out_data_mngment/data_for_final_analysis_agg_cpi/agg_cpi_exp_series_p90")
real_exp_10=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p10")
real_exp_90=pd.read_pickle("../out_data_mngment/data_for_final_analysis/exp_series_p90")

data={'real_90_agg': real_exp_90_agg_cpi, 
      'real_10': real_exp_10,
      'real_90': real_exp_90
      }

#sort data and save to one data frame
df_sorted=real_exp_10_agg_cpi.sort_values(['year', 'month'])
for t in data.keys():
    df_sorted=pd.merge(df_sorted, data[t], on = ['year', 'month'])
df_sorted['time'] = df_sorted[['year', 'month']].apply(lambda x: '/'.join(x), axis=1)
    
    
for c in [2,3]:
    # figure for poor
    plt.plot(df_sorted['time'], df_sorted.T.iloc[c],'--', label="Aggregate CPI ",color='orange',linewidth=2,scalex =False)
    plt.plot( df_sorted['time'], df_sorted.T.iloc[c+2],'--', label="Heterogeneous CPI",color='blue')
    plt.legend(loc=3)
    #x=df_sorted['time']
    #plt.fill_between(df_sorted['time'], df_sorted['exp_p1-p10_agg'],df_sorted['exp_p1-p10'],color='red')
    plt.xticks(df_sorted['time'][::8],rotation=70)
    plt.xlabel("Time")
    plt.ylabel("Real Consumption")
    plt.savefig("../out_figures/comparison_evolution/"+df_sorted.columns[c],bbox_inches='tight')
    plt.clf()


# all in one
for c in range(2,5,2):   
    plt.plot(df_sorted['time'], df_sorted.T.iloc[c],'--', label="Poor ",color='orange',linewidth=2,scalex =False)
    plt.plot( df_sorted['time'], df_sorted.T.iloc[c+1],'--', label="Rich",color='blue')
    plt.legend(loc=3)
    #x=df_sorted['time']
    #plt.fill_between(df_sorted['time'], df_sorted['exp_p1-p10_agg'],df_sorted['exp_p1-p10'],color='red')
    plt.xticks(df_sorted['time'][::8],rotation=70)
    plt.xlabel("Time")
    plt.ylabel("Real Consumption")
    plt.savefig("../out_figures/comparison_evolution/"+df_sorted.columns[c]+ "_rich_vs_poor",bbox_inches='tight')
    plt.clf()