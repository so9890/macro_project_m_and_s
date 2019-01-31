
"""
Functions

@author: sdobkowitz
"""

def _cum_distribution(d):
    """ Calculate cummulative distribution function.
    
    Returns sorted data set with cummulative weights and the cummulative 
    distribution function.
    
    d= data set containing samplingt weights and income for a given month-year
    
    """
    
    n= d['FINLWT21'].sum()
    d_sorted= d.sort_values('VALUE', na_position= 'first')
    d_sorted['index_sorted']= range(len(d_sorted))
    d_sorted['Cum_weights']=""
    d_sorted['Percentage_below_equal']=""
        
    cum_weight=0.0   
    s=0
    number_skipped=0
    for i in range(0,len(d_sorted)): 
        # if-statement to skip those observations that have 
        # had the same value as the previous one.
        if s== 0: # note that s ==0 only in the initial round. 
            number_skipped = 0
        else:
            number_skipped +=s-1
        j= i+number_skipped

        # This is the actual loop.
        # cum_weight_previous = cum_weight 
        s = 0
        while j <len(d_sorted) and d_sorted['VALUE'].iloc[j]==d_sorted['VALUE'].iloc[j+s]: 
             
             cum_weight += d_sorted['FINLWT21'].iloc[j+s]
             s+=1 
             
             if j+s==len(d_sorted): # if so, the next value to be tested would be out of range.
                 break
             else:
                 continue
            
        d_sorted['Cum_weights'].iloc[j:j+s] = cum_weight # the end value is exlcuded! 
        d_sorted['Percentage_below_equal'].iloc[j:j+s]= cum_weight/n

    return d_sorted


#####################################################
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