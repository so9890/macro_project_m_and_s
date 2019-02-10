""" Local Projections estimation and impulse response functions plotting

"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
stdev=pd.read_pickle("../data_for_final_analysis/data_inequality")["sd"]
gini_coeff=pd.read_pickle("../data_for_final_analysis/data_inequality")["gini"]
p_9010=pd.read_pickle("../data_for_final_analysis/data_inequality")["90-10"]
mp_shocks=pd.read_csv("../original_data/mp_shocks/RR_series.csv")

    

# regression is super easy


#reg1 = sm.OLS(y,x,)
#results = reg1.fit()
#params=reg1.fit().params


## to be done:
#1. in a loop y=ineq.loc[h:]['sd'].val-ineq.loc[0:len[ineq]-(h+1)]
#2. x=control and shocks
#3. save params