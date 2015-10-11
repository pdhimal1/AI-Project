'''
File:
	company_name.py
Authors:
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get name of the company using the company's stock ticker symbol
'''


import pandas as pd

'''
Opens Stock.csv from Data to find the company name
	- uses linear search
@param-ticker
@returns name of the company, N/A if not found
'''

def find_name(ticker):
	
	#read_csv will open and close the file	
	df = pd.read_csv('../Data/Stock.csv')
	
	
	company = ticker
	company = company.upper()
	index = -1

	for i in range(len(df)):
	    test = df["Ticker"][i].upper()
	    if test == company:
		index = i;

	if index is not -1:
		return df["Name"][index]
	else:
		return "N/A"



