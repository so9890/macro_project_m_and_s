""" File holding code that I took out of original code, might be useful again later."""
""" Add description of UCC codes to ITBI files """


#now merge info on UCC from CE_dictionary
helperI = pd.DataFrame(data=pd.read_excel('../CEX_Data_Documentation/CE_dictionary.xlsx', sheet_name=2).loc[:,'Survey':'Code Description'])


# there are only two survey types
#keep all INTERVIEW entries
helperI = helperI.drop(helperI.loc[:,'Survey'][~helperI.loc[:,'Survey'].str.contains('INTERVIEW')].index)

helperI= helperI.drop(helperI.loc[:,'File'][~helperI.loc[:,'File'].str.contains('(I|i)(T|t)(b|B)(I|i)')].index)
# note that ITBI imputed is only relevant for years 2004-2005! so drop for this analysis
helperI= helperI.drop(helperI.loc[:,'File'][helperI.loc[:,'File'].str.contains('m')].index)
# only keep if Variable name == UCC using a regular expression to make sure not losing any entry due to misspelling 
helperI = helperI.drop(helperI.loc[:,'Variable Name'][~helperI.loc[:,'Variable Name'].str.contains('(U|u)(c|C)(c|C)')].index)
# note there is only UCC now in the file
# and all Code Values are unique

# now only keep those observations in UCC_Description that are in data 
# the following dataframe contains all UCC that are in the data and their descriptions
# it can be used to check what items we add up as income
#unique_UCC_description=helperI[ np.isin(  helperI['Code Value'].astype(int).values, unique_UCC['UCC'].values)]
#print(unique_UCC_description['Code Description'])

""" Merge Code Description to data"""
# make Code Value in helperI an integer
helperI['Code Value'] = helperI['Code Value'].astype(int)
data=data.merge(helperI[['Code Value','Code Description']], left_on= 'UCC', right_on= 'Code Value', how= 'left')

""" There are strange UCCs in the income file. I wonder whether I can add them all up.... There is also the """
""" Can """

#match_NEWID= data[data['NEWID']==657965]

    
""" The following is to debug the weighted_percentile function.

Note that the version below does not give the sum of weights for a given income.

 """

setup = setup_fun()
d=setup['d']
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
        d_sorted['Percentage_below_equal'].iloc[j:j+s]= cum_weight/n

        if j+s == len(d_sorted):
            break
        else:
            continue


""" From concordance file. Manual part.  """


con = pd.read_excel('../../original_data/Concordance/CPI_item_id_UCC_WilliamCassey_CPIRequirementsOfCE.xlsx' , header=None, usecols = "A:B", names =['concordance_sheet','Drop'])

# page numbers in con.concordance_sheet have a nan in Drop!
con=pd.DataFrame(data=con.concordance_sheet[~pd.isna(con.Drop)], columns= ['concordance_sheet'])
con.index = range(0,len(con))

#------------------------------------------------------------------------
## Split column containing code into UCC and CPI item_id.
## Note that CPI codes are strings and UCCs are integers. 
#------------------------------------------------------------------------

con['UCC'] = ""
con['item_id']=""

for i in range(0,len(con)):
    if isinstance(con.concordance_sheet[i], int):
        con.UCC[i]=con.concordance_sheet[i]
    else:
        con.item_id[i]= con.concordance_sheet[i]

# only keep concordance

con=con[['concordance_sheet','item_id','UCC']]

#------------------------------------------------------------------------
## Merge item_id from CPI file. Only keep data that we have in the CPI 
## file.
#------------------------------------------------------------------------

# unique list of items in CPI file
c_CPI_unique = pd.DataFrame(data=d_CPI['concordance_id'].unique(), columns=['concordance_id'])
c_CPI_unique['Identifier']="In CPI"
con=con.merge(c_CPI_unique, left_on= 'item_id', right_on= 'concordance_id', how= 'left')
con.Identifier[con.concordance_id=='']=""

#------------------------------------------------------------------------
# the variable Identifier in con is "nan" whenever the item_id (CPI)
# is not in our data set. It is, this is an ELI and we only have 
# Item stratum price level information. 
# CAUTION: if all item_ids of a category get dropped by dropping nans,
# ie. >=2 nans after another, then the UCCs will be assigned to a wrong 
# preceding item.
#------------------------------------------------------------------------

con['BoolIII']=""
for i in range(0,len(con)):
    if pd.isna(con.Identifier.iloc[i]):
        if pd.isna(con.Identifier.iloc[i+1])| pd.isna(con.Identifier.iloc[i-1]) :
            con['BoolIII'][i]=True
        else:
            con['BoolIII'][i]=False
    else:
        con['BoolIII'][i]=""

     
# in case BoolIII is True then the UCCs should be assigned to the next higher
# category of that we have CPI information. This ensures that all UCC in the 
# concordance files will at least have a CPI counterpart. The next higher 
# category is always given by two letters. Create a column with the first two 
# letters of item_id. After all two letters there are numbers. Thw two letters
# give the 'Expenditure class'.
        
# first, drop if Identifier == nan and BoolIII False, then the above explained
# issue does not apply. 
        
con=con[con['BoolIII']!=False]

# drop the second of the two following item_ids without match in CPI
con['BoolIV']=""
for i in range(0,len(con)):
    if con.BoolIII.iloc[i]:
        if con.BoolIII.iloc[i+1]:
            con.BoolIV.iloc[i+1]=True
            
con=con[con.BoolIV!=True]

# merge  the categories with no macth in CPI to their expenditure class.
reggae =re.compile('\d+')
con.index=range(0,len(con))

for i in range(0,len(con)):
    if con.BoolIII.iloc[i]==True:
        con['item_id'].iloc[i]=reggae.split(con['item_id'].iloc[i])[0]
    else:
        con['item_id'].iloc[i]=con['item_id'].iloc[i]
# drop superfluous columns
con=con[['item_id', 'UCC']]

#------------------------------------------------------------------------
## For concordance fill up empty cells in column item_id with previous entry. 
## this will match item stratum and UCC codes. 
#------------------------------------------------------------------------

    
for i in range(0,len(con)):
    if re.search('(\w|\d)',con.item_id.iloc[i]):
        con.item_id.iloc[i]=con.item_id.iloc[i]
    else:
        con.item_id.iloc[i]=con.item_id.iloc[i-1]

con = con[con.UCC!=""]
con.index=range(0,len(con))
con.to_pickle('../../original_data/Concordance/concordance_final')


#------------------------------------------------------------------------
## Test whether the con.UCC only contains unique items. 
## It does not. Thus, keep a list of duplicates and decide on where to 
## match multiply named UCCs. This is important because consumers only 
## spent their amount once and not twice.
#------------------------------------------------------------------------

UCC_u =pd.DataFrame(data= con.UCC.unique(), columns=['unique_UCCs'])

dups = con[con.UCC.duplicated(keep=False)] # keep= False marks all duplicates as True 
print('There are', len(UCC_u)-1, 'unique UCCs in the concordance file, and', len(dups.UCC.unique()) ,'are reported more then once.' )

pd.DataFrame(dups[['item_id','UCC']].sort_values('UCC')).to_excel('../../original_data/tb_printed/duplicates_UCC.xlsx')
# dupplicates in terms of item_id and UCC can be dropped. they exist because 
# on ELI level they are not duplicates but as we cannot differentiate between 
# them on item-stratum we can pick one.

# identify second and higher order duplicates and drop them. Keep first one. 
con['dup']=con.duplicated()
con=con[['item_id','UCC']][con.dup==False]
con.index=range(0,len(con))

# For those items where only the UCC is a cuplicate. Match the UCC to the 
# respective expenditure class.
# This is reasonable as the expenditure class price level is a weighted
# aggregate of the corresponding item-stratum price levels.

con['dupsII'] = con.UCC.duplicated(keep=False)

reggae =re.compile('\d+')

for i in range(0,len(con)):
    if con.dupsII.iloc[i]:
        con['item_id'].iloc[i]=reggae.split(con['item_id'].iloc[i])[0]
 
# drop duplicates in terms of item_id and UCC, keep first observation of each 
# duplicate group.

con['dup']=con[['item_id','UCC']].duplicated()
con=con[['item_id','UCC']][con.dupsII==False]

# verify there are no duplicates in terms of UCC in the concordance file.

assert len(con)==len(con.UCC.unique())
print ('There are no UCC duplicates in the concordance file. All expenditures \
will be assigned a unique price level.')


#------------------------------------------------------------------------
## Merge concordance file to CPI file. 
#------------------------------------------------------------------------

d_CPI=d_CPI.merge(con, left_on= 'concordance_id', right_on= 'item_id', how= 'left')
# check whether all observations in d_CPI could have been merged, 
# whether merge was correct
print('There are', len(d_CPI['UCC'][pd.isna(d_CPI['series_id'])]), 'unmerged CPI observations.' )

# check which prices could not be merged. Ensure these are broader categories only.
not_merged=d_CPI[['concordance_id','Description', 'item_id_y']]
not_merged=not_merged[pd.isna(not_merged.item_id_y)]
not_merged=not_merged.drop_duplicates('concordance_id')

not_merged['Boolean']=""
for i in range(0, len(not_merged)):
    if re.search('\d+',not_merged.concordance_id.iloc[i]):
        not_merged['Boolean'].iloc[i]=True
    else:
        not_merged['Boolean'].iloc[i]=False
not_merged=not_merged[not_merged.Boolean]
# 76 CPI codes of smaller categories were not listed in the concordance file.

#save
not_merged[['concordance_id','Description']].to_excel('../../original_data/tb_printed/not_merged_CPIs.xlsx')

#------------------------------------------------------------------------
## Clean CPI file to only contain prices that could have been merged to 
## UCC codes.
#------------------------------------------------------------------------

d_CPI = d_CPI[~pd.isna(d_CPI.item_id_y)]
d_CPI = d_CPI[['series_id', 'year', 'value', 'period', 'Description', 'concordance_id', 'UCC']]
d_CPI.UCC=d_CPI.UCC.astype(float)


""" From CPI_preparation"""
###############################################################################

#------------------------------------------------------------------------
## Read in and clean series identifier, merge it to data sets.
#------------------------------------------------------------------------

series_id = pd.read_excel('../../original_data/CPI_Data/item_encoding_II.xlsx')
series_id.columns=['item_id', 'else_else']

# 1) The second column contains first the item description followed by a number
# and additional things. Only filter the description before the first number.
# 2) On top, drop too broad categories starting with SA 

regex= re.compile('[0-9]+')
series_id['Description']=""

series_id['Boolean']=""


for i in range(0,len(series_id)):
    series_id['Description'].iloc[i]=regex.split(series_id.else_else.iloc[i])[0]
    
    if re.search('^SA{1}', series_id.item_id.iloc[i]):
        series_id['Boolean'].iloc[i]=False
        
    else:
       series_id['Boolean'].iloc[i]=True
       
series_id = series_id[['item_id','Description', 'Boolean']]

# Merge series_id item_code and data/data_q 'series_id' to check whether extraction worked. 

data=data.merge(series_id, left_on= 'item_id', right_on= 'item_id', how= 'left')

data = data[data.Boolean]

