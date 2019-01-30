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