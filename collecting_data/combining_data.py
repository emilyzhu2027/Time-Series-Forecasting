# combining all data files into mega data file
from cmath import nan
import pandas as pd
import os, glob
import functools as ft

def import_stock_data(filename):
    df = pd.read_csv(filename)
    if df.empty:
        return df
    else:
        df.columns = ["date", df.columns[1] + "_closingprice"]

        return df

def import_sentiment_data(filename):
    df = pd.read_csv(filename)
    df = df.drop(columns = ["Unnamed: 0"])

    fileCSV = filename.split("/")[1]
    stockTicker = fileCSV.split("_")[0]

    df = df.set_index(['date']).add_prefix(stockTicker + '_').reset_index()

    return df

def import_commodity_data(filename):
    df = pd.read_csv(filename)

    df = df.drop(columns = ["Open", "High", "Low", "Vol.", "Change %"])
    df['Date'] = pd.to_datetime(df['Date'], format = "%m/%d/%Y").dt.date

    fileCSV = filename.split("/")[1]
    commodityName = fileCSV.split("_")[0]

    df.rename(columns={'Price': commodityName + "_closingprice", 'Date': 'date'}, inplace=True)

    return df

def main():
    listOfAllData = []
    for filename in glob.glob(os.path.join("webscraped_data", '*.csv')):
        # stock + currency data
        dfData = import_stock_data(filename)
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
    fullData.to_csv("full_data.csv")

main()
