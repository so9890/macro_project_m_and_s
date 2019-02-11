""" Local Projections estimation and impulse response functions plotting

"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

stdev = pd.read_pickle("../data_for_final_analysis/data_inequality")["sd"]
gini_coeff = pd.read_pickle("../data_for_final_analysis/data_inequality")["Gini"]
p_9010 = pd.read_pickle("../data_for_final_analysis/data_inequality")["90-10"]

b = np.zeros((3, 20))
st_dev = np.zeros((3, 20))
for i, k in [stdev, gini_coeff, p_9010]:
    x_1 = k.shift(1) - k.shift(2)
    x_1.name = "l_1"
    x_2 = k.shift(2) - k.shift(3)
    x_2.name = "l_2"
    X = pd.concat([x_1, x_2], axis=1)
    X["const"] = 1
    # x_1=k.loc[2:].values-k.loc[0:len(k)-3].values
    #    x_2=k.loc[3:].values-k.loc[0:len(k)-4].values
    for h in range(20):
        y = k.shift(-h) - k.shift(-(h - 1))
        reg = sm.OLS(
            endog=y,
            exog=X.loc[0:len(y)][["const", "l_1", "l_2", "rr_l0", "rr_l1", "rr_l2"]],
            missing="drop",
        ).fit()
        b[i, h] = reg.params[3]
        st_dev[i, h] = reg.bse[3]


# regression is super easy

# reg1 = sm.OLS(y,x,)
# results = reg1.fit()
# params=reg1.fit().params


# to be done:
# 1. in a loop y=ineq.loc[h:]['sd'].val-ineq.loc[0:len[ineq]-(h+1)]
# 2. x=control and shocks
# 3. save params
