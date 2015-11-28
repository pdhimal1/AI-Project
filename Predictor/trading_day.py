
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
def get_trading_day(company, scaler, useSpread, useVolume):
	
	opening_price = float(company.get_open())
	todays_volume = float(company.get_volume())
	high = float(company.get_days_high())
	low = float(company.get_days_low())
	avg_volume = float(company.get_avg_daily_volume())
        change = float(company.get_change())
	
	if useSpread is False and useVolume is False:
		today = np.array((opening_price, high, low))
	elif useSpread is True and useVolume is False:
		today = np.array((opening_price, high, low, change))
	elif useSpread is False and useVolume is True:
		today = np.array((opening_price, high, low, todays_volume))
	else:
		today = np.array((opening_price, high, low, change, todays_volume))

	scaled_today = scale.scale(today, scaler)

	return today, scaled_today
