'''
Usage: 
	predictor.py <ticker> <num_days>


Arguments:
	<ticker> - ticker symbol for the company
		 DJIA  if you want predictions for all 30 companies in DJIA
	<num_days> - number of days to grab historical data
'''

from datetime import datetime
from datetime import date as dt
from datetime import timedelta

from docopt import docopt
import numpy as np
from sklearn import svm
from yahoo_finance import Share

import company_name as cn
import get_historical as gh
import trading_day as td
import djia

def get_dates(num_days):
	
	today = dt.today()
	yesturday = today - timedelta(days =1)

	date2 = today- timedelta(days = num_days)
	yest = yesturday.isoformat()
	date2 = date2.isoformat()	
	
	return date2, yest

def print_info(company, ticker, predict):

	date = company.get_trade_datetime()
	
	#get company name
	name = cn.find_name(ticker)

	print "\n",  name, "[" , ticker, "]"  
	print "Predicted [closing] price for", date[:10], ": $", predict[0]
	company.refresh()

	#change = (company.get_price() - company.get_open())/company.get_open()
	#print change

	print "current price                              $", company.get_price()
	print
	#print "% change today ", 

def process_company(ticker, num_days):
	#initialize share with the company ticker
	company = Share(ticker)
	
	day1, day2 = get_dates(num_days)

	

	historical = company.get_historical(day1, day2)
	#print len(historical), "Days of historical data"

	#reverse the list 
	historical.reverse()
	
	#get training and target data
	training, target = gh.training_data(historical, company)

	#get current trading day's data
	this_day = td.get_trading_day(company)	

	#--------------------------------------------------------------------#
	clf = svm.SVR()

	#Fit takes in data (#_samples X #_of_features array), and target(closing - 1 X #_of_Sample_size array)

	clf.fit(training,target)
	
	#predict takes in today's 
	predict = clf.predict(this_day)

	print_info(company, ticker, predict)

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
	
 

if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)


