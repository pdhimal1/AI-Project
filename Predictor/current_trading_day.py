'''
File: 
	current_trading_day.py
Authors: 
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get current trading day's data for a given company
'''
import numpy as np
import normalize as scale

'''
@param - company_info - dictionary with company info from yfinance
@return today - stacked array (opening price, high, low, today's volume and average volume)
'''
def get_trading_day(company_info, scaler, useSpread, useVolume):
	
	opening_price = float(company_info.get('open', 0))
	todays_volume = float(company_info.get('volume', 0))
	high = float(company_info.get('dayHigh', 0))
	low = float(company_info.get('dayLow', 0))
	avg_volume = float(company_info.get('averageVolume', 0))
	change = float(company_info.get('regularMarketChange', 0))
	
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
