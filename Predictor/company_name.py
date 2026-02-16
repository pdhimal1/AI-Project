'''
File:
	company_name.py
Authors:
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get name of the company using the company's stock ticker symbol
'''


import pandas as pd
import os

'''
Opens Stock.csv from Data to find the company name
	- uses linear search
@param-ticker
@returns name of the company, N/A if not found
'''

def find_name(ticker):
	# Try to read from CSV first
	csv_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Stock.csv')
	
	if os.path.exists(csv_path):
		try:
			df = pd.read_csv(csv_path)
			company = ticker.upper()
			
			for i in range(len(df)):
				test = str(df["Ticker"][i]).upper()
				if test == company:
					return df["Name"][i]
		except Exception:
			pass
	
	# Fallback: try HDF5 file if it exists
	h5_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'ticker_database.h5')
	if os.path.exists(h5_path):
		try:
			import tables as tb
			data_in = tb.open_file(h5_path, mode='r')
			table_in = data_in.root.group.table
			index = -1
			name = "N/A"
			for x in table_in.iterrows():
				if x['ticker'] == ticker:
					name = x['name']
					index = x.nrow
			data_in.close()
			if index != -1:
				return name
		except Exception:
			pass
	
	# Return ticker if no name found
	return ticker

def get_djia_list():
	# Try to read from CSV first
	csv_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'DJIA_ticker.csv')
	
	if os.path.exists(csv_path):
		try:
			df = pd.read_csv(csv_path)
			if 'Ticker' in df.columns:
				return df['Ticker'].tolist()
			else:
				# Try first column
				return df.iloc[:, 0].tolist()
		except Exception:
			pass
	
	# Fallback: try HDF5 file if it exists
	h5_path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'ticker_database.h5')
	if os.path.exists(h5_path):
		try:
			import tables as tb
			data_in = tb.open_file(h5_path, mode='r')
			array = data_in.root.djia_tickers.Djia_Tickers
			ticker = []
			for x in range(len(array)):
				ticker.append(array[x])
			return ticker
		except Exception:
			pass
	
	# Default DJIA list if file not found
	return ['AAPL', 'MSFT', 'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'HD', 'INTC',
			'KO', 'VZ', 'DIS', 'MRK', 'AXP', 'CSCO', 'NKE', 'CVX', 'WBA', 'MCD',
			'XOM', 'BA', 'GS', 'CAT', 'IBM', 'TRV', 'MMM', 'DOW', 'RTX', 'AMGN']

