'''
Python module to get current trading prices for a given company
'''
import numpy as np

'''
@param - company 
@return today - stacked array (opening price, high, low, today's volume and average volume)
'''
def get_trading_day(company):
	
	opening_price = company.get_open()
	todays_volume = company.get_volume()
	high = company.get_days_high()
	low = company.get_days_low()
	avg_volume = company.get_avg_daily_volume()

	today = np.array((opening_price, high, low, todays_volume, avg_volume))

	return today
