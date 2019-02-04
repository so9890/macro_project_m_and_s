""" CPI_CE concordance. """

import pandas as pd


concordance = pd.read_excel('../../original_data/Concordance/ucc_pce_concordance_2017.xlsx', names= ['UCC','Source' ,'ELI_Description', 'PCE', 'PCE_Description'], usecols= "A:E")
concordance =concordance[2:]


""" Here is how to read in pdf files: https://automatetheboringstuff.com/chapter13/"""
text = tx.process("../../original_data/Concordance/pce-cpi-code-mapping.pdf")