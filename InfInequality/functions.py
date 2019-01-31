
"""
Functions

@author: sdobkowitz
"""
import pandas as pd
def _cum_distribution(d):
    """ Calculate cummulative distribution function.
    
    Returns sorted data set with cummulative weights and the cummulative 
    distribution function.
    
    d= data set containing samplingt weights and income for a given month-year
    
    """
    
    d_sorted= d.sort_values('VALUE', na_position= 'first')
    d_sorted.index= range(len(d_sorted))
    d_sorted['Cum_weights']=""
        
    cum_weight=0.0   
    s=0
    number_skipped=0
    for i in range(0,len(d_sorted)): 
        # if-statement to skip those observations that have 
        # had the same value as the previous one.
        if s== 0 and i==0: 
            number_skipped = 0
        else:
            number_skipped +=s-1
        j= i+number_skipped

        # This is the actual loop.
        # cum_weight_previous = cum_weight 
        s = 0
        while  d_sorted['VALUE'].iloc[j]==d_sorted['VALUE'].iloc[j+s]: 
             
             cum_weight += d_sorted['FINLWT21'].iloc[j+s]
             s+=1 
             
             if j+s==len(d_sorted): # if so, the next value to be tested would be out of range.
                 break
             else:
                 continue
            
        d_sorted['Cum_weights'].iloc[j:j+s] = cum_weight # the end value is exlcuded! 
        #d_sorted['Percentage_below_equal'].iloc[j:j+s]= cum_weight/n

        if j+s == len(d_sorted):
            break
        else:
            continue
        
    n= d['FINLWT21'].sum()    
    d_sorted['Percentage_below_equal']= d_sorted['Cum_weights']/n
    #also calculate the point 
    Percentage_equal= d_sorted.groupby('VALUE').agg({'VALUE':['min'], 'FINLWT21': ['sum']})
    Percentage_equal.columns=['VALUE','Percentage_equal']
    d_sorted=d_sorted.merge(Percentage_equal, left_on= 'VALUE', right_on= 'VALUE', how= 'left')
    
    return d_sorted


#####################################################
def _percentiles(d_sorted):
    """ Calculate household-specific percentiles. 
    
    Follow the cummulative distribution function derived in function _cum_distribution.
    
    d_sorted is the data set resulting from the function _cum_distribution.
    
    """ 
    
    d_sorted['Percentile']=""
    start = 0
   
    for i in range(start,len(d_sorted)):
   
            if d_sorted['Percentage_below_equal'] < p/100 : # all observations with a value of which to observe equal or smaller values fall within the given percentile
                 d_sorted['Percentile'].iloc[i]=p
"""CONTINUE"""
            elif d_sorted['Percentage_below_equal'].iloc[i] >= p/100 and 1-d_sorted['Percentage_below_equal'].iloc[i]+d_sorted['Percentage_equal'].iloc[i]>=1-p/100: # at threshold, the second condition says that the 
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