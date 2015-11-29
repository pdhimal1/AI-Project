'''
File:
	company_name.py
Authors:
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get name of the company using the company's stock ticker symbol
'''


import pandas as pd
import tables as tb

'''
Opens Stock.csv from Data to find the company name
	- uses linear search
@param-ticker
@returns name of the company, N/A if not found
'''
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
'''

def find_name(ticker):
	data_in = tb.open_file("../Data/ticker_database.h5", mode='r')
	table_in = data_in.root.group.table
	index = -1
	for x in table_in.iterrows():
        	if x['ticker'] == ticker:
            		name = x['name']
			index = x.nrow
	data_in.close()
	if index is not -1:
		return name
	else:
		return "N/A"

def get_djia_list():
	ticker = []
	data_in = tb.open_file("../Data/ticker_database.h5", mode='r')
	array = data_in.root.djia_tickers.Djia_Tickers
	for x in range(len(array)):
   		ticker.append(array[x])

	#data_in.close()
	return ticker
	

