import pandas as pd

def find_name(ticker):
	
	df = pd.read_csv('secwiki_tickers.csv')
	
	
	company = ticker
	company = company.upper()
	index = -1

	for i in range(len(df)):
	    test = df["Ticker"][i]
	    if test == company:
		index = i;

	if index is not -1:
		return df["Name"][index]
	else:
		return "N/A"



