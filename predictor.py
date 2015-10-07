'''
Usage: 
	predictor.py <ticker> <start_date> <end_date>

Arguments:
	
'''

from datetime import datetime
from docopt import docopt
from yahoo_finance import Share
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import company_name as cn
from sklearn import svm

#to get all opening prices together
def get_historical_opening(historical):

    opening = [] #is a dynamic array (list) for python
    
    for i in range(len(historical)):
        x = historical[i]['Open']
        opening.append(x)
        
    return opening

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


def main(args):
	ticker = args['<ticker>']
	start = args['<start_date>']
	end = args['<end_date>']

	date1 = datetime.strptime(start, "%m-%d-%Y").strftime("%Y-%m-%d")
	date2 = datetime.strptime(end, "%m-%d-%Y").strftime("%Y-%m-%d")

	company = Share(ticker)

	historical = company.get_historical(date1, date2)
	#print len(historical), "Days of historical data"

	#reverse the list 
	historical.reverse()

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

	opening_price = company.get_open()
	todays_volume = company.get_volume()
	high = company.get_days_high()
	low = company.get_days_low()
	avg_volume = average_volume[0]

	today =np.array((opening_price, high, low, todays_volume, avg_volume))

	clf = svm.SVR()

	#Fit takes in data (#_samples X #_of_features array), and target(closing - 1 X #_of_Sample_size array)
	clf.fit(data,closing)

	predict = clf.predict(today)


	date = company.get_trade_datetime()
	name = cn.find_name(ticker)

	print "\n",  name, "[" , ticker, "]"  
	print "Predicted [closing] price for", date[:10], ": $", predict[0]
	company.refresh()

	#change = (company.get_price() - company.get_open())/company.get_open()
	#print change

	print "current price                              $", company.get_price()
	print
	#print "% change today ", 
 

if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)


