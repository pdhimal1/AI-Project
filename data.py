"""
	Usage: 
		data.py <ticker>
		data.py -h
		data.py --help
	Arguments:
		<ticker> - ticker symbol for the company
		
"""
from yahoo_finance import Share
import numpy as np
import matplotlib.pyplot as plt
from docopt import docopt

#import sklearn

def print_data(company):
	#date and time of the trade
	date = company.get_trade_datetime()

	#opening price
	opening_price = company.get_open()

	#Price right now (Yahoo finance is delayed by 15 mins)
	current_price = company.get_price()

	#Day's high and low prices 
	day_high = company.get_days_high()
	day_low = company.get_days_low()
	#price changes from opening price
	price_change = company.get_change()

	print "trading date: ", date
	print "current price: ", current_price
	print "opening price: $" , opening_price
	print "day high: $", day_high
	print "day low: $", day_low
	print "print price change: $", price_change

def main(main): 
	ticker = args['<ticker>']
	company = Share(ticker)
	print_data(company)
	

if __name__ == "__main__":
	args = docopt(__doc__)
	#print arguements
	main(args)


