"""
Emily Zhu
Time Series Forecasting Project
Description: This file combines all the webscraped and downloaded data from the 'downloaded_data', 
'sentiment_data', and 'webscraped_data' folders into one csv file called 'full_data.csv'.
"""

from cmath import nan
import pandas as pd
import os, glob
import functools as ft

def import_price_data(filename):
    """
    Parameters: 
        filename (str), the name of the file containing the closing price data for a currency or stock
    Function:
        Retrieves the data from the csv file name and alters the column names to a uniform format 
        for the date and make clear which currency/stock is being represented
    Return Val:
        df (Pandas DataFrame), contains closing price data and dates for one stock/currency
    """

    df = pd.read_csv(filename)
    if df.empty:
        return df
    else:
        df.columns = ["date", df.columns[1] + "_closingprice"]

        return df

def import_sentiment_data(filename):
    """
    Parameters: 
        filename (str), the name of the file containing the sentiment scores for a stock
    Function:
        Retrieves the data from the csv file name and alters the column names to include the
        stock ticker
    Return Val:
        df (Pandas DataFrame), contains sentiment scores and dates for one stock
    """

    df = pd.read_csv(filename)
    df = df.drop(columns = ["Unnamed: 0"])

    fileCSV = filename.split("/")[1]
    stockTicker = fileCSV.split("_")[0]

    df = df.set_index(['date']).add_prefix(stockTicker + '_').reset_index()

    return df

def import_commodity_data(filename):
    """
    Parameters: 
        filename (str), the name of the file containing the sentiment scores for a commodity
    Function:
        Retrieves the data from the csv file name, keeps the closing price and date, and alters the 
        column names to include the commodity name
    Return Val:
        df (Pandas DataFrame), contains closing prices and associated dates for one commodity
    """

    df = pd.read_csv(filename)

    df = df.drop(columns = ["Open", "High", "Low", "Vol.", "Change %"])
    df['Date'] = pd.to_datetime(df['Date'], format = "%m/%d/%Y").dt.date

    fileCSV = filename.split("/")[1]
    commodityName = fileCSV.split("_")[0]

    df.columns = ["date", commodityName + "_closingprice"]
    df = df.astype({"date": str})
    
    return df

def main():
    """
    Parameters: 
        None
    Function:
        Reads in all csv files from the data folders, changes the column names, and combines them
        into one csv file called 'full_data.csv'
    Return Val:
        None
    """
    listOfAllData = []

     # stock + currency data
    for filename in glob.glob(os.path.join("webscraped_data", '*.csv')):
        dfData = import_price_data(filename)
        listOfAllData.append(dfData)
       
    # commodity data
    for filename in glob.glob(os.path.join("downloaded_data", '*.csv')):
        dfData = import_commodity_data(filename)
        listOfAllData.append(dfData)

    # stock sentiment data
    for filename in glob.glob(os.path.join("sentiment_data", '*.csv')):
        dfData = import_sentiment_data(filename)
        listOfAllData.append(dfData)
    
    listOfAllData = [df for df in listOfAllData if not df.empty]

    for data in listOfAllData:
        print(data.columns)


    fullData = ft.reduce(lambda  left,right: pd.merge(left,right,on=['date'], how='outer'), listOfAllData)

    fullData = fullData.dropna(how = 'all')
    fullData.to_csv("full_data.csv")

main()
