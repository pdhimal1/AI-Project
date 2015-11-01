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
	Python source file to make stock predictions using support vector machine. This program takes in <ticker> (ticker symbol for the company) and <num_days> (number of days to get historical data) from the command line. It uses yahoo_finance module to get stock data from yahoo finance, preprocess the data and send them to support vector machine as training data, target data, and prediction_day data to make the prediction. The program then outputs name of the company, ticker symbol, predicted closing price and current price of the stock	
'''
from datetime import datetime
from datetime import date as dt
from datetime import timedelta
import sys
from socket import gethostbyname, gaierror

from docopt import docopt
import numpy as np
from sklearn import svm
from yahoo_finance import Share

import company_name as cn
import get_historical as gh
import trading_day as td
import djia
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
	
	return date2, yest

'''
Outputs name of the company, ticker symbol, predicted closing price and current price to standard output
@param - company, ticker, predict
@returns - none
'''
def print_info(company, ticker, predict):

	date = company.get_trade_datetime()
	
	#get company name
	name = cn.find_name(ticker)

	print "\n",  name, "[" , ticker, "]"  
	print "Predicted [closing] price for", date[:10], ": $ %.2f " % predict[0]
	company.refresh()

	#change = (company.get_price() - company.get_open())/company.get_open()
	#print change

	print "current price                              $", company.get_price()
	print
	#print "% change today ", 

'''
Creates company Share object, gets historical prices, preprocess them and send them to support vector machine

@param - ticker
	num_days
@returns
	none

'''
def process_company(ticker, num_days):
	#initialize share with the company ticker
	try:
		company = Share(ticker)

	except (gaierror):
		print "\nNot connected!\n"
		sys.exit()
	
	day1, day2 = get_dates(num_days)

	

	historical = company.get_historical(day1, day2)
	#print len(historical), "Days of historical data"

	#reverse the list 
	historical.reverse()

	#print len(historical)
	
	unscaled_opening = gh.get_unscaled_opening(historical)
	
	#--------------------------------#
	scaler = scale.get_scaler(unscaled_opening)

	#get training and target data
	training, target, scaled_training, scaled_target = gh.training_data(historical, company, scaler)

	#get current trading day's data
	this_day, scaled_today = td.get_trading_day(company, scaler)	


	#--------------------------------------------------------------------#
	clf = svm.SVR(gamma=0.001, C=0.01) # gamma = 0.00000001 for 10 days

	#Fit takes in data (#_samples X #_of_features array), and target(closing - 1 X #_of_Sample_size array)

	clf.fit(scaled_training,scaled_target)
	
	#predict takes in today's 
	predict = clf.predict(this_day)

	#print_info(company, ticker, predict)

	clf.fit(scaled_training,scaled_target)
	predict = clf.predict(scaled_today)
	#print predict
	pre = scaler.inverse_transform(predict)

	
	#print "Using scaled data"
	print_info(company, ticker, pre)

'''

'''
def gui_call(ticker, days):
	num_days = days

	DJIA = 'djia'

	if ticker.upper() == DJIA.upper():
		tickers = djia.get_djia_list()
		for i in range(len(tickers)):
			process_company(tickers[i], num_days)
	else:	
		process_company(ticker, num_days)

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
		tickers = djia.get_djia_list()
		for i in range(len(tickers)):
			process_company(tickers[i], num_days)
	else:	
		process_company(ticker, num_days)

'''
Calls Main.
Uses Docopt module to parse the command line arguments
'''
 

if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)


