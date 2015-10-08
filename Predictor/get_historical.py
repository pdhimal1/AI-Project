'''
Python module to get historical prices and volumes for a given company
'''

import numpy as np

'''

'''
#to get all opening prices together
def get_historical_opening(historical):

    opening = [] #is a dynamic array (list) for python
    
    for i in range(len(historical)):
        x = historical[i]['Open']
        opening.append(x)
        
    return opening
'''

'''

def get_historical_high(historical):

    days_high = []

    for i in range(len(historical)):
        x = historical[i]['High']
        days_high.append(x)

    return days_high

def get_historical_low(historical):
    days_low = [] 

    for i in range(len(historical)):
        x = historical[i]['Low']
        days_low.append(x)

    return days_low

def get_historical_closing(historical):

    #same for closing    
    closing = [] 
    
    for i in range(len(historical)):
        x = historical[i]['Close']
        closing.append(x)
        
    return closing

def get_historical_volume(historical, company):
    historical_volume = [] #is a dynamic array (list) for python
    average_volume = []

    for i in range(len(historical)):
        x = historical[i]['Volume']
        historical_volume.append(x)
        average_volume.append(company.get_avg_daily_volume())
    return historical_volume, average_volume


'''
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

