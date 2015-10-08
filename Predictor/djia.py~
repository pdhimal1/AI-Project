import pandas as pd

def get_djia_list():

	df = pd.read_csv('../Data/DJIA_ticker.csv')
	
	

	ticker = []

	for i in range(len(df)):
		temp = df['Ticker'][i]
		ticker.append(temp)
	return ticker
	

