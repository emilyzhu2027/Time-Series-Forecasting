"""
Emily Zhu
Time Series Forecasting Project
Description: This file imports data from "full_data.csv" (from the collecting_data folder) and runs 
some processing on it before using the data to train and test a LSTM model.
"""
import tensorflow as tf
import pandas as pd
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint
from numpy import concatenate
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def data_preprocessing(rawData):
    """
    Parameters: 
        rawData (Pandas DataFrame), contains data on stock closing prices, stock sentiment scores, 
        currency closing prices, and commodity closing prices collected via webscraping and downloading
    Function:
        Cleans data by evenly spacing time series data, adjusting the time intervals, calculating the target 
        variable, and filling in missing data
    Return Val:
        finalData (Pandas DataFrame), contains weekly data on select closing prices and sentiment scores
    """
    # Ensuring that time series data and time index is evenly spaced
    rangeOfDates = pd.date_range(start='7/03/2018', end='7/03/2023').strftime("%Y-%m-%d")
    emptyDfWAllDates = pd.DataFrame(columns = rawData.columns)
    emptyDfWAllDates["date"] = rangeOfDates

    missingDates = list(set(rawData.index.to_list())-set(emptyDfWAllDates.index.to_list()))
    concatDf = emptyDfWAllDates[emptyDfWAllDates["date"].isin(missingDates)]
    fullDataAllDates = pd.concat([rawData, concatDf])

    # Filling all NaN values with 0
    fullDataAllDates = fullDataAllDates.fillna(0)

    fullDataAllDates.date = pd.to_datetime(fullDataAllDates.date)
    fullDataAllDates.set_index("date", inplace = True)

    # Ensuring that all values in dataset are floats instead of strings
    for c in fullDataAllDates:
        strCol = fullDataAllDates[c].astype(str).str
        strCol = strCol.replace(',', '')
        fullDataAllDates[c] = strCol.astype(float)
    fullDataAllDates = fullDataAllDates.apply(pd.to_numeric)

    # Narrowing down the data to the range selected at the beginning
    correctDateRangeDf = fullDataAllDates[fullDataAllDates.index >= '2018-07-03']
    correctDateRangeDf = correctDateRangeDf[correctDateRangeDf.index <= '2023-07-03']
    
    # Change daily data to weekly data
    monthDataDf = correctDateRangeDf.resample('W').mean()

    # Keeping columns that have less than 50% of the data as 0
    finalData = pd.DataFrame()
    numHalfRows = int(len(monthDataDf.index)/2) + 1
    for colName in monthDataDf:
        if (monthDataDf[colName] == 0).sum() <= numHalfRows:
            finalData[colName] = monthDataDf[colName]

    # Calculating the target y variable - whether or not Nike stocks are going up (1) or down (0)
    finalData["NKE_TargetY"] = (finalData["NKE_closingprice"].pct_change().shift(-1) > 0).astype(int)
    finalData = finalData.drop(columns = ["NKE_closingprice", "Unnamed: 0"])

    return finalData

def series_to_supervised(dataDf, n_in=1, n_out=1, dropnan=True):
    """
    Parameters: 
        dataDf (Pandas DataFrame), data being used for LSTM model
        n_in (int), number of time frames prior to use in analysis of the current time frame
        n_out (int), number of time frames after to use in analysis of the current time frame
        dropnan (boolean), whether or not to drop NaN values
    Function:
        Creates columns that contain data before and after the current time frame's variables to help predict
        the current time frame's target variable
    Return Val:
        agg (Pandas DataFrame), data containing all variables with additional time frames
    Credit for Function:
        https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/
    """

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
    """
    Parameters: 
        finalData (Pandas DataFrame), contains data for LSTM
    Function:
        Scales data, and trains and tests LSTM model
    Return Val:
        None
    """
    # Scaling data
    scaler = MinMaxScaler(feature_range=(0,1))
    scaledData = scaler.fit_transform(finalData)
    scaledDataDf = pd.DataFrame(scaledData, columns = finalData.columns, index = finalData.index)

    scaledDataReframed = series_to_supervised(scaledDataDf.drop(columns = ["NKE_TargetY"]))
    print(scaledDataReframed.index)

    # Splitting data into train and test
    splitIndex = int(len(scaledDataReframed.index) * 0.67)
    X = scaledDataReframed.copy()
    y = scaledDataDf.copy()["NKE_TargetY"].to_frame()
    y = y.drop(index = ["'2023-07-09'"])

    X_test = X.iloc[splitIndex:, :]
    X_train = X.iloc[:splitIndex, :]
    y_test = y.iloc[splitIndex:, :]
    y_train = y.iloc[:splitIndex, :]

    X_train = X_train.values.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_test = X_test.values.reshape((X_test.shape[0], 1, X_test.shape[1]))

    # Callbacks - saving best model in case LSTM breaks and stopping when the model stops improving
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5), 
        ModelCheckpoint('best_so_far.h5', monitor='val_loss', save_best_only='True', verbose=2)]
    
    # LSTM model
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2]), dropout = 0.1, recurrent_dropout = 0.1),
        tf.keras.layers.Dense(1)])
    model.compile(loss='mae', optimizer='adam')

    model.fit(X_train, y_train, validation_split = 0.2, epochs=50, batch_size=30, validation_data=(X_test, y_test), verbose = 2, callbacks = callbacks)

def main():
    """
    Parameters: 
        None
    Function:
        Transforms data and creates LSTM model to predict direction of Nike stocks
    Return Val:
        None
    """

    rawData = pd.read_csv("collecting_data/full_data.csv")
    print(rawData.head())
    fullData = data_preprocessing(rawData)
    print(fullData.head())
    LSTM(fullData)
    
main()