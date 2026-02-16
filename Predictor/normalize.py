from sklearn import preprocessing
import numpy as np

def get_scaler(opening):
	min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1,1))
	opening_array = np.array(opening).reshape(-1, 1)
	min_max_scaler.fit(opening_array)
	return min_max_scaler
	
	
def scale(data, scaler):
	
	
	data_train = scaler.transform(data.reshape(-1, 1))
	#scaler_data = scaler.transform(data)

	#print scaler_data.mean(axis = 0)
	#print data_scaled

	#print "Mean ", data_train.mean(axis = 0)
	#print "Std ", data_train.std(axis = 0)

	return data_train.flatten()


def scale_today(data, scaler):	
	
	data_train = scaler.transform(data.reshape(-1, 1))

	return data_train.flatten(), scaler
