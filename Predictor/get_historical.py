'''
File: 
	get_historical.py
Authors: 
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get historical prices and volumes for a given company
'''

import numpy as np
import normalize as scale


'''
@param - historical - list containing historical prices, and volumes
@retruns opening - list containing daily opening prices from the historical data
'''
#to get all opening prices together
def get_unscaled_opening(historical):

	opening = [] #is a dynamic array (list) for python
	
	for i in range(len(historical)):
		x = float(historical[i]['Open'])
		opening.append(x)		
	return opening

'''
@param - historical - list containing historical prices, and volumes
@retruns opening, scaled_opening - list containing daily opening prices from the historical data
'''
def get_historical_opening(historical, scaler):

	opening = [] #is a dynamic array (list) for python
	
	for i in range(len(historical)):
		x = float(historical[i]['Open'])
		opening.append(x)

	scaled_opening = scale.scale(np.array(opening), scaler)
		
	return opening, scaled_opening

'''
@param - historical - list containing historical prices, and volumes
@retruns days_high - list containing daily high prices from the historical data
'''
def get_historical_high(historical, scaler):

	days_high = []

	for i in range(len(historical)):
		x = float(historical[i]['High'])
		days_high.append(x)

	scaled_high = scale.scale(np.array(days_high), scaler)
		
	return days_high, scaled_high

'''
@param - historical - list containing historical prices, and volumes
@retruns days_low - list containing daily low prices from the historical data
'''

def get_historical_low(historical, scaler):
	days_low = [] 

	for i in range(len(historical)):
		x = float(historical[i]['Low'])
		days_low.append(x)

	scaled_low = scale.scale(np.array(days_low), scaler)
		
	return days_low, scaled_low


'''
@param - historical - list containing historical prices, and volumes
@retruns closing - list containing daily closing prices from the historical data
'''
def get_historical_closing(historical, scaler):

	#same for closing	
	closing = [] 
	
	for i in range(len(historical)):
		x = float(historical[i]['Adj_Close'])
		closing.append(x)
		
	scaled_closing = scale.scale(np.array(closing), scaler)

	return closing, scaled_closing


'''
@param - historical - list containing historical prices, and volumes
	- company_info - dict with company info from yfinance
@retruns - historical_volume - list containing daily volume from the historical data
	- average_volume - list containing average volume for the sample data
'''
def get_historical_volume(historical, company_info, scaler):
	historical_volume = [] #is a dynamic array (list) for python
	average_volume = []

	avg_vol = company_info.get('averageVolume', 0)

	for i in range(len(historical)):
		x = float(historical[i]['Volume'])
		historical_volume.append(x)
		average_volume.append(float(avg_vol))

	scaled_historical_volume = scale.scale(np.array(historical_volume), scaler)

	scaled_average_volume = scale.scale(np.array(average_volume), scaler)

	return historical_volume, average_volume, scaled_historical_volume, scaled_average_volume

'''
@param - historical - list containing historical prices, and volumes
	- scaler
@return change - price change for the day
	_scaled_change - price change scaled for -1 to 1

'''
def get_change(historical, scaler):
	change = []
	change.append(0)
	for i in range(len(historical)-1):
		x = float(historical[i+1]["Close"]) - float(historical[i]['Close'])
		change.append(x)
	scaled_change = scale.scale(np.array(change), scaler)

	return change, scaled_change

def calculate_sma(data, window):
	"""Calculate Simple Moving Average"""
	if len(data) < window:
		return [np.mean(data)] * len(data)
	sma = []
	for i in range(len(data)):
		if i < window - 1:
			sma.append(np.mean(data[:i+1]))
		else:
			sma.append(np.mean(data[i-window+1:i+1]))
	return sma

def calculate_ema(data, window):
	"""Calculate Exponential Moving Average"""
	if len(data) < window:
		return [np.mean(data)] * len(data)
	
	ema = [np.mean(data[:window])]
	multiplier = 2 / (window + 1)
	
	for i in range(window, len(data)):
		ema.append((data[i] - ema[-1]) * multiplier + ema[-1])
	
	# Pad beginning with first EMA value
	ema = [ema[0]] * (window - 1) + ema
	return ema

def calculate_rsi(data, window=14):
	"""Calculate Relative Strength Index"""
	if len(data) < window + 1:
		return [50] * len(data)
	
	deltas = [0]
	for i in range(1, len(data)):
		deltas.append(data[i] - data[i-1])
	
	gains = [max(0, d) for d in deltas]
	losses = [abs(min(0, d)) for d in deltas]
	
	rsi = [50] * window
	
	avg_gain = np.mean(gains[1:window+1])
	avg_loss = np.mean(losses[1:window+1])
	
	for i in range(window, len(data)):
		avg_gain = (avg_gain * (window - 1) + gains[i]) / window
		avg_loss = (avg_loss * (window - 1) + losses[i]) / window
		
		if avg_loss == 0:
			rsi.append(100)
		else:
			rs = avg_gain / avg_loss
			rsi.append(100 - (100 / (1 + rs)))
	
	return rsi

def calculate_bollinger_bands(data, window=20, num_std=2):
	"""Calculate Bollinger Bands"""
	if len(data) < window:
		return data, data, data
	
	sma = calculate_sma(data, window)
	upper_band = []
	lower_band = []
	
	for i in range(len(data)):
		if i < window - 1:
			std = np.std(data[:i+1])
		else:
			std = np.std(data[i-window+1:i+1])
		
		upper_band.append(sma[i] + (std * num_std))
		lower_band.append(sma[i] - (std * num_std))
	
	return upper_band, sma, lower_band

def calculate_macd(data, fast=12, slow=26, signal=9):
	"""Calculate MACD (Moving Average Convergence Divergence)"""
	if len(data) < slow:
		return [0] * len(data), [0] * len(data), [0] * len(data)
	
	ema_fast = calculate_ema(data, fast)
	ema_slow = calculate_ema(data, slow)
	
	macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
	signal_line = calculate_ema(macd_line, signal)
	histogram = [m - s for m, s in zip(macd_line, signal_line)]
	
	return macd_line, signal_line, histogram

def get_technical_indicators(historical, scaler):
	"""Calculate technical indicators for enhanced predictions"""
	closing_prices = [float(h['Close']) for h in historical]
	
	# Moving averages
	sma_20 = calculate_sma(closing_prices, 20)
	ema_12 = calculate_ema(closing_prices, 12)
	
	# RSI
	rsi = calculate_rsi(closing_prices, 14)
	
	# Bollinger Bands
	bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(closing_prices, 20)
	
	# MACD
	macd_line, signal_line, histogram = calculate_macd(closing_prices)
	
	# Scale indicators
	scaled_sma_20 = scale.scale(np.array(sma_20), scaler)
	scaled_ema_12 = scale.scale(np.array(ema_12), scaler)
	scaled_rsi = scale.scale(np.array(rsi), scaler)
	scaled_macd = scale.scale(np.array(macd_line), scaler)
	
	return (sma_20, ema_12, rsi, macd_line), (scaled_sma_20, scaled_ema_12, scaled_rsi, scaled_macd)

'''
def get_range():

'''

'''
Method to stack training data together
	stacks opening, volume, high,low,average_volume together 
	result is traing data array of (sample size X # of features)
	and target array of (sample size X 1)
@param historical list, company_info - dict from yfinance
@returns data - training data
	closing - target data

'''
def training_data(historical, company_info, scaler, useSpread, useVolume, useTechIndicators=True):

	historical_opening, scaled_opening = get_historical_opening(historical, scaler)
	historical_closing, scaled_closing = get_historical_closing(historical, scaler)
	historical_high, scaled_high = get_historical_high(historical, scaler)
	historical_low, scaled_low = get_historical_low(historical, scaler)
	historical_volume, average_volume, scaled_volume, scaled_avg_vol = get_historical_volume(historical, company_info, scaler)
	change, scaled_change = get_change(historical, scaler)

	opening =  np.array(historical_opening)
	_scaled_opening =  np.array(scaled_opening)

	volume = np.array(historical_volume)
	_scaled_volume = np.array(scaled_volume)

	high = np.array(historical_high)
	_scaled_high = np.array(scaled_high)

	low = np.array(historical_low)
	_scaled_low = np.array(scaled_low)

	avg_vol = np.array(average_volume)
	_scaled_avg_vol = np.array(scaled_avg_vol)

	closing = np.array(historical_closing)
	_scaled_closing = np.array(scaled_closing)

	_change = np.array(change)
	_scaled_change = np.array(scaled_change)
	
	# Base features
	if useSpread is False and useVolume is False:
		data = np.vstack((opening, high, low))
		scaled_data = np.vstack((_scaled_opening, _scaled_high, _scaled_low))
	elif useSpread is True and useVolume is False:
		data = np.vstack((opening, high, low, _change))
		scaled_data = np.vstack((_scaled_opening, _scaled_high, _scaled_low, _scaled_change))
	elif useSpread is False and useVolume is True:
		data = np.vstack((opening, high, low, volume))
		scaled_data = np.vstack((_scaled_opening, _scaled_high, _scaled_low, _scaled_volume))
	else:
		data = np.vstack((opening, high, low, _change, volume))
		scaled_data = np.vstack((_scaled_opening, _scaled_high, _scaled_low, _scaled_change, _scaled_volume))
	
	# Add technical indicators if enabled
	if useTechIndicators and len(historical) >= 20:
		(sma_20, ema_12, rsi, macd_line), (scaled_sma_20, scaled_ema_12, scaled_rsi, scaled_macd) = get_technical_indicators(historical, scaler)
		
		_sma_20 = np.array(sma_20)
		_ema_12 = np.array(ema_12)
		_rsi = np.array(rsi)
		_macd = np.array(macd_line)
		
		_scaled_sma_20 = np.array(scaled_sma_20)
		_scaled_ema_12 = np.array(scaled_ema_12)
		_scaled_rsi = np.array(scaled_rsi)
		_scaled_macd = np.array(scaled_macd)
		
		data = np.vstack((data, _sma_20, _ema_12, _rsi, _macd))
		scaled_data = np.vstack((scaled_data, _scaled_sma_20, _scaled_ema_12, _scaled_rsi, _scaled_macd))

	shape1, shape2 = data.shape
	data = data.reshape(shape2, shape1)

	shape1, shape2 = scaled_data.shape
	scaled_data = scaled_data.reshape(shape2, shape1)

	return data, closing, scaled_data, _scaled_closing

