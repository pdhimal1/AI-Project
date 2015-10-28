from sklearn import preprocessing
import numpy as np

def get_scaler(opening):
	min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1,1))
	min_max_scaler.fit(opening)
	return min_max_scaler
	
	
def scale(data, scaler):

	
	data_train = scaler.transform(data)
	#scaler_data = scaler.transform(data)

	#print scaler_data.mean(axis = 0)
	#print data_scaled

	#print "Mean ", data_train.mean(axis = 0)
	#print "Std ", data_train.std(axis = 0)

	return data_train


def scale_today(data, scaler):	
	
	#min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1,1))
	data_train = scaler.transform(data)
	#scaler_data = scaler.transform(data)

	#print scaler_data.mean(axis = 0)
	#print data_scaled

	#print "Today's Mean ", data_train.mean(axis = 0)
	#print "Today's Std ", data_train.std(axis = 0)

	return data_train, min_max_scaler
