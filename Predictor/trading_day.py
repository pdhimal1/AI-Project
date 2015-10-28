
'''
File: 
	trading_day.py
Authors: 
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get current trading prices for a given company
'''
import numpy as np
import normalize as scale

'''
@param - company 
@return today - stacked array (opening price, high, low, today's volume and average volume)
'''
def get_trading_day(company, scaler):
	
	opening_price = float(company.get_open())
	todays_volume = float(company.get_volume())
	high = float(company.get_days_high())
	low = float(company.get_days_low())
	avg_volume = float(company.get_avg_daily_volume())

	today = np.array((opening_price, high, low))

	scaled_today = scale.scale(today, scaler)

	return today, scaled_today
