
"""
Functions

@author: sdobkowitz
"""

def _values_percentiles(n,d_sorted, value, percentile, weight, CW, Per_below, p):

    start = 0
    cum_weight = 0.0
    
    for i in range(start,len(value)+1):
    # first, while loop to assign correct weight, taking into account sum of weights of observations with the same value. 
            cum_weight_previous = cum_weight
            
            s = 0
            while value.iloc[i]==value.iloc[i+s]: 
                
                cum_weight += weight.iloc[i+s]
                s+=1 # s will thus have a value s.th. observation i+s is not yet included. 
                
            CW.iloc[i:i+s] = cum_weight # the end value is exlcuded! 
            Per_below.iloc[i:i+s]= cum_weight/n
            
   # second, if-statement to check for the relevant percentile 
   # note that cum_weight gives the cummulative weight taking all equal observations into account
   
            if cum_weight/n < p/100 : # all observations with a value of which to observe equal or smaller values fall within the given percentile
                percentile.iloc[i:i+s]=p
                            
            elif cum_weight/n >= p/100 and (1-cum_weight_previous/n)>=1-p/100: # at threshold, the second condition says that the 
                                                                                                      # probability to observe an equal or higher income
                                                                                                      # is >= 1-p/100. This is required since the data is 
                                                                                                      # discrete. 
                percentile.iloc[i:i+s]=p
            
            else: 
                start = (i)   # since at the point of the break i+s is the index of the first observation that 
                                  # has not yet been assigned a percentile 
                                  # this is from where the operation has to start from for the next percentile.
    
                cum_weight=CW.iloc[(i-1)]      # the loop stops, ie. income of household i, has already been added
                                                                      # we have to ensure that the next loop starts from 
                                                                      # the previous cumulative value! Otherwise weight 
                                                                      # added twice!
                break

    print('percentile', p, 'done!')

    return 