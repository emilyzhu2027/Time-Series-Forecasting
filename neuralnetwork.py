import tensorflow as tf
import pandas as pd
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint
from numpy import concatenate
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# Credits: https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/

def data_preprocessing(rawData):
    # nike stock up or down - y variable
    rawData["NKE_TargetY"] = (rawData["NKE_closingprice"].pct_change().shift(-1) > 0).astype(int)
    rawData = rawData.drop(columns = ["NKE_closingprice"])

    # imputation for fields with less than 50% missing - https://drnesr.medium.com/filling-gaps-of-a-time-series-using-python-d4bfddd8c460
    percentMissingPerCol = pd.DataFrame({"column_name": rawData.columns, "percent_missing": rawData.isnull().sum() * 100 / len(rawData)})
    dataOver50 = percentMissingPerCol[percentMissingPerCol["percent_missing"] >= 0.5]
    finalData = dataOver50.assign(InterpolateTime=dataOver50.target.interpolate(method='time'))

    return finalData

def series_to_supervised(dataDf, n_in=1, n_out=1, dropnan=True):
    colNames = dataDf.columns.to_list()
    data = dataDf.values

    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('%s(t-%d)' % (colNames[j], i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('%s(t)' % (colNames[j])) for j in range(n_vars)]
        else:
            names += [('%s(t+%d)' % (colNames[j], i)) for j in range(n_vars)]
    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg

def LSTM(finalData):
    scaler = MinMaxScaler(feature_range=(0,1))
    scaledData = scaler.fit_transform(finalData)

    scaledDataReframed = series_to_supervised(scaledData)
    print(scaledDataReframed.head())

    splitIndex = len(scaledDataReframed.index) * 0.67
    X = scaledDataReframed.copy().drop(columns = ["NKE_TargetY"])
    y = scaledDataReframed.copy()["NKE_TargetY"]

    X_test = X[splitIndex:, :]
    X_train = X[:splitIndex, :]
    y_test = y[splitIndex:, :]
    y_train = y[:splitIndex, :]

    X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5), 
        ModelCheckpoint('best_so_far.h5', monitor='val_loss', save_best_only='True', verbose=2)]
    
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2]), dropout = 0.1, recurrent_dropout = 0.1),
        tf.keras.layers.Dense(1)])
    model.compile(loss='mae', optimizer='adam')

    model.fit(X_train, y_train, validation_split = 0.2, epochs=50, batch_size=30, validation_data=(X_test, y_test), verbose = 2, callbacks = callbacks)


    y_predict = model.fit(X_test)
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[2]))
    # invert scaling for forecast
    inv_Y_Pred = concatenate((y_predict, X_test[:, 1:]), axis=1)
    inv_Y_Pred = scaler.inverse_transform(inv_Y_Pred)
    inv_Y_Pred = inv_Y_Pred[:,0]
    # invert scaling for actual
    y_test = y_test.reshape((len(y_test), 1))
    inv_Y_Test = concatenate((y_test, X_test[:, 1:]), axis=1)
    inv_Y_Test = scaler.inverse_transform(inv_Y_Test)
    inv_Y_Test = inv_Y_Test[:,0]
    # calculate RMSE
    rmse = sqrt(mean_squared_error(inv_Y_Test, inv_Y_Pred))
    print('Test RMSE: %.3f' % rmse)

    

def main():
    rawData = pd.read_csv("/collecting_data/full_data.csv")
    fullData = data_preprocessing(rawData)
    LSTM(fullData)
    
