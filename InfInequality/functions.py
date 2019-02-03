
""" Functions.

    1) Functions to derive income percentiles. Used in CEX_DATA_percentiles.py
    2) Function to assign quarters and collapse price data on quarterly level in CPI_DATA_preparation.py 


"""
###############################################################################
""" 1) """

def weights_percentiles(d):
    """ Calculate the percentile of each household.
    
    1) Sum up weights grouped by income value.
    2) Derive cummulative distribution and probibility distribution functions.
    3) Assign percentiles to each household.
            
    d is the data set

    """
    d_distribution = _cum_distribution(d)
    d_sorted = _percentiles(d_distribution)
    
    return d_sorted


###############################################################################
def _cum_distribution(d):
    """ Calculate cummulative distribution function.
    
    Return sorted data set with cummulative weights and the cummulative 
    distribution function and probability distribution.
    
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
    
    #also calculate probability distribution and the probability to observe an income equal or bigger
    Observations_equal= d_sorted.groupby('VALUE').agg({'VALUE':['min'], 'FINLWT21': ['sum']})
    Observations_equal.columns=['VALUE','Percentage_equal']
    Observations_equal['Percentage_equal']= Observations_equal['Percentage_equal']/n
    d_sorted=d_sorted.merge(Observations_equal, left_on= 'VALUE', right_on= 'VALUE', how= 'left')
    d_sorted['Percentage_equal_above']= 1- d_sorted['Percentage_below_equal'] + d_sorted['Percentage_equal']
    
    return d_sorted


###############################################################################
    
def _percentiles(d_sorted):
    """ Calculate household-specific percentiles. 
    
    Follow the distribution functions derived in function _cum_distribution.
    
    d is the data set resulting from the function _cum_distribution.
    
    """ 
    
    d_sorted['Percentile']=""
    start=0
    
    for p in range(1,101, 1):
        
        for i in range(start,len(d_sorted)):
   
            if d_sorted['Percentage_below_equal'].iloc[i] < p/100 : 
                # all observations with a probability to observe equal or 
                # smaller values lower then p/100 fall within the given percentile
                d_sorted['Percentile'].iloc[i]=p

            elif d_sorted['Percentage_below_equal'].iloc[i] >= p/100 and d_sorted['Percentage_equal_above'].iloc[i]>=1-p/100: 
                # at threshold, the second condition says that the 
                # probability to observe an equal or higher income
                # is >= 1-p/100. This is required since the data is 
                # discrete. 
                d_sorted['Percentile'].iloc[i]=p
            
            else: 
                # since at the point of the break i is the index of the first observation that 
                # has not yet been assigned a percentile 
                # this is from where the operation has to start for the next percentile.
                start = i

                break
            #break
        print('Percentile', p, 'done!')

    return d_sorted


###############################################################################
    
""" 2) """
    
def _quarter_collapse(data):
    """ Identify quarter of observation and collapse on quarterly level. 
    
    Use the quarterly mean of the CPI value when collapsing data set.
    
    data is the input data. 
    
    """
    for j in range(0,10,3):
        for i in range(1+j,4+j,1):
            if i <10:
                data.loc[data['period'].str.contains('0'+str(i)), 'quarter'] = 1+j/3
            else:
                data.loc[data['period'].str.contains(str(i)), 'quarter'] = 1+j/3

    # collapse dataset on series_id, year and quarter level
    data_q=data.groupby(['series_id', 'year', 'quarter', 'item_id', 'Description'], as_index = False).agg({'value': 'mean'})
    
    return data_q
    