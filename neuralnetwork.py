import tensorflow as tf
import pandas as pd
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint

def data_preprocessing(rawData):
    # nike stock up or down - y variable
    rawData["NKE_TargetY"] = (rawData["NKE_closingprice"].pct_change().shift(-1) > 0).astype(int)

    # imputation for fields with less than 50% missing - https://drnesr.medium.com/filling-gaps-of-a-time-series-using-python-d4bfddd8c460
    percentMissingPerCol = pd.DataFrame({"column_name": rawData.columns, "percent_missing": rawData.isnull().sum() * 100 / len(rawData)})
    dataOver50 = percentMissingPerCol[percentMissingPerCol["percent_missing"] >= 0.5]


    finalData = dataOver50.assign(InterpolateTime=dataOver50.target.interpolate(method='time'))

    # standarad scaler
    return finalData

def train_test_split(finalData):
    X_train, y_train = create_dataset(train_data, window_size)
    X_test, y_test = create_dataset(test_data, window_size)

def train_model(X_train, y_train):
    callbacks = [EarlyStopping(monitor='val_loss', patience=5)]
    
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(4, input_shape=(), dropout = 0.1, recurrent_dropout = 0.1),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(num_words, activation='softmax')])

    model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam())

    # Train the model
    model.fit(X_train, y_train, epochs=50, batch_size=64, callbacks = callbacks)

    model_lstm.compile(optimizer="RMSprop", loss="mse")

def test_model(model, X_test, y_test):
    test_predictions = []
    for i in range(len(X_test)):
        test_predictions.append(model.predict(np.array([X_test[i]]))[0][0])


    
