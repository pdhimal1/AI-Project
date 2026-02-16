'''
Usage: 
	predictor.py <ticker> <num_days>


Arguments:
	<ticker> - ticker symbol for the company
		 DJIA  if you want predictions for all 30 companies in DJIA
	<num_days> - number of days to grab historical data

Examples:
	python predictor.py aapl 30
	python predictor.py djia 10
	python predictor.py DJIA 5
'''

'''
File:
	Predictor.py
Authors:
	 Prakash Dhimal, Kevin Sanford
Description:
	Python source file to make stock predictions using support vector machine. This program takes in <ticker> (ticker symbol for the company) and <num_days> (number of days to get historical data) from the command line. It uses yfinance module to get stock data from yahoo finance, preprocess the data and send them to support vector machine as training data, target data, and prediction_day data to make the prediction. The program then outputs name of the company, ticker symbol, predicted closing price and current price of the stock	
'''

from datetime import datetime
from datetime import date as dt
from datetime import timedelta

import sys
from socket import gethostbyname, gaierror

from docopt import docopt
import numpy as np
from sklearn import svm
import yfinance as yf

import company_name as cn
import get_historical as gh
import current_trading_day as td
import trading_day as trading_cal
import normalize as scale


'''
Based on the number of dates provided, this method will return starting date (in yyyy-mm-dd format) and ending date (same format) to get the historical data
Uses datetime module to get current data, day before, and starting day (day before - number of days)

@param - num_days - number of days
@returns
	- date2 - starting day (in yyyy-mm-dd format)
	- yest - days before (yesturday's date)
'''
def get_dates(num_days):
	
	today = dt.today()
	yesturday = today - timedelta(days =1)

	date2 = today- timedelta(days = num_days)
	yest = yesturday.isoformat()
	date2 = date2.isoformat()
	# Format for yfinance
	return date2[:10], yest[:10]

'''
Outputs name of the company, ticker symbol, predicted closing price and current price to standard output
@param - company, ticker, predict
@returns - none
'''
def print_info(company_info, ticker, predict):
	# Get next trading day for prediction date
	next_trading = trading_cal.get_next_trading_day()
	date_str = trading_cal.format_trading_day_with_weekday(next_trading)
	
	#get company name
	name = cn.find_name(ticker)
	str1 = "\n" +  name + "[" + ticker + "]"
	print("\n", name, "[", ticker, "]")
	sys.stderr.write(str1)
	str2 = "\nPredicted [closing] price for " + date_str + ": $ %.2f " % predict[0]
	print("Predicted [closing] price for", date_str, ": $ %.2f " % predict[0])
	sys.stderr.write(str2)

	#get current price from info
	current_price = company_info.get('currentPrice') or company_info.get('regularMarketPrice', 'N/A')
	print("Current price                              $", current_price)
	sys.stderr.write(("\nCurrent price                             $ " + str(current_price)))
	print()
	sys.stderr.write("\n")

'''
Creates company ticker object, gets historical prices, preprocess them and send them to support vector machine

@param - ticker
	num_days
@returns
	none

'''
def process_company(ticker, num_days, useSpread, useVolume, useTechIndicators=True):
	#initialize ticker with yfinance
	try:
		company = yf.Ticker(ticker)
		# Test if we can get info
		company_info = company.info
		if not company_info:
			print("\nError: Could not fetch data for ticker:", ticker)
			return

	except Exception as e:
		print("\nError connecting or fetching data:", str(e))
		sys.exit()
	
	day1, day2 = get_dates(num_days)

	# Get historical data using yfinance
	historical = company.history(start=day1, end=day2)
	
	# Convert to list of dictionaries format expected by other functions
	historical_list = []
	for index, row in historical.iterrows():
		historical_list.append({
			'Open': row['Open'],
			'High': row['High'],
			'Low': row['Low'],
			'Close': row['Close'],
			'Adj_Close': row['Close'],  # yfinance already provides adjusted close
			'Volume': row['Volume']
		})

	if len(historical_list) == 0:
		print("Error! Please check your inputs and try again")
		return
	
	else:
		#reverse the list 
		historical_list.reverse()

		unscaled_opening = gh.get_unscaled_opening(historical_list)
	
		#--------------------------------#
		scaler = scale.get_scaler(unscaled_opening)
	
		#get training and target data
		training, target, scaled_training, scaled_target = gh.training_data(historical_list, company_info, scaler, useSpread, useVolume, useTechIndicators)
	

		#get current trading day's data
		this_day, scaled_today = td.get_trading_day(company_info, scaler, useSpread, useVolume, useTechIndicators)	
		
		# Reshape to 2D array (1 sample x n features) for sklearn
		scaled_today = scaled_today.reshape(1, -1)

		#--------------------------------------------------------------------#
		clf = svm.SVR(gamma=0.000001, C=1e3, kernel='rbf') # gamma = 0.00000001 for 10 days

		#Fit takes in data (#_samples X #_of_features array), and target(closing - 1 X #_of_Sample_size array)

		clf.fit(scaled_training, scaled_target)
	
		#predict takes in today's data
		predict = clf.predict(scaled_today)
		pre = scaler.inverse_transform(predict.reshape(-1, 1)).flatten()

		print_info(company_info, ticker, pre)

'''
'''
def gui_call(ticker, days, spreadV, volumeV, techV=1):
	num_days = days
	
	useSpread = False	
	useVolume = False
	useTech = True

	if (spreadV == 1):
		useSpread = True
	if (volumeV == 1):
		useVolume = True
	if (techV == 0):
		useTech = False
	DJIA = 'djia'

	if ticker.upper() == DJIA.upper():
		tickers = cn.get_djia_list()
		for i in range(len(tickers)):
			process_company(tickers[i], num_days, useSpread, useVolume, useTech)
	else:	
		process_company(ticker, num_days, useSpread, useVolume, useTech)

'''
Main - driver of the program. Parses the command line arguments and calls precess company for given stock (based on ticker)
	if 'djia' is entered calls process_company for all 30 companies in Dow Jones Industrial Average
'''
def main(args):

	ticker = args['<ticker>']
	num_days = args['<num_days>']
	num_days = int(num_days)
	
	DJIA = 'djia'
	
	if ticker.upper() == DJIA.upper():
		tickers = cn.get_djia_list()
		for i in range(len(tickers)):
			process_company(tickers[i], num_days, True, False, True)
	else:	
		process_company(ticker, num_days, True, False, True)

'''
Calls Main.
Uses Docopt module to parse the command line arguments
'''
if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)
