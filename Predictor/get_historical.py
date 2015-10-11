'''
File: 
	get_historical.py
Authors: 
	Prakash Dhimal, Kevin Sanford
Description:
	Python module to get historical prices and volumes for a given company
'''

import numpy as np

'''
@param - historical - list containing historical prices, and volumes
@retruns opening - list containing daily opening prices from the historical data
'''
#to get all opening prices together
def get_historical_opening(historical):

    opening = [] #is a dynamic array (list) for python
    
    for i in range(len(historical)):
        x = historical[i]['Open']
        opening.append(x)
        
    return opening

'''
@param - historical - list containing historical prices, and volumes
@retruns days_high - list containing daily high prices from the historical data
'''
def get_historical_high(historical):

    days_high = []

    for i in range(len(historical)):
        x = historical[i]['High']
        days_high.append(x)

    return days_high

'''
@param - historical - list containing historical prices, and volumes
@retruns days_low - list containing daily low prices from the historical data
'''

def get_historical_low(historical):
    days_low = [] 

    for i in range(len(historical)):
        x = historical[i]['Low']
        days_low.append(x)

    return days_low


'''
@param - historical - list containing historical prices, and volumes
@retruns closing - list containing daily closing prices from the historical data
'''
def get_historical_closing(historical):

    #same for closing    
    closing = [] 
    
    for i in range(len(historical)):
        x = historical[i]['Close']
        closing.append(x)
        
    return closing


'''
@param - historical - list containing historical prices, and volumes
	- company - Share object
@retruns - historical_volume - list containing daily volume from the historical data
	- average_volume - list containing average volume for the sample data
'''
def get_historical_volume(historical, company):
    historical_volume = [] #is a dynamic array (list) for python
    average_volume = []

    for i in range(len(historical)):
        x = historical[i]['Volume']
        historical_volume.append(x)
        average_volume.append(company.get_avg_daily_volume())
    return historical_volume, average_volume


'''
Method to stack training data together
	stacks opening, volume, high,low,average_volume together 
	result is traing data array of (sample size X # of features)
	and target array of (sample size X 1)
@param historical list, company - Share object
@returns data - training data
	closing - target data

'''
def training_data(historical, company):

	historical_opening = get_historical_opening(historical)
	historical_closing = get_historical_closing(historical)
	historical_high = get_historical_high(historical)
	historical_low = get_historical_low(historical)
	historical_volume, average_volume = get_historical_volume(historical, company)

	opening =  np.array(historical_opening)
	volume = np.array(historical_volume)
	high = np.array(historical_high)
	low = np.array(historical_low)
	avg_vol = np.array(average_volume)

	closing = np.array(historical_closing)

	data = np.vstack((opening, high, low, volume, avg_vol))

	shape1, shape2 = data.shape
	data = data.reshape(shape2, shape1)

	return data, closing

