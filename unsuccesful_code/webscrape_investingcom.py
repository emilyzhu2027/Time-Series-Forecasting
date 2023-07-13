import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
from random import randint

def getPayload(startDate, endDate, dataFreq, commodityName):
    print("GET PAYLOAD")
    # pulled from investing.com - api calls when changing date
    commodityIDNums = {
        "gold": 8830,
        "silver": 8836,
        "copper": 8831,
        "brent-oil": 8833,
        "crude-oil": 8849,
        "natural-gas": 8862,
        "heating-oil": 8988,
        "us-cotton-no.2": 8851
    }

    startDate = urllib.parse.quote(startDate, safe='')
    endDate = urllib.parse.quote(endDate, safe='')
    payload = {
            "curr_id": str(commodityIDNums[commodityName]),
            "smlID": str(randint(1000000, 99999999)),
            "st_date": startDate,
            "end_date": endDate,
            "interval_sec": dataFreq,
            "sort_col": "date",
            "sort_ord": "DESC",
            "action": "historical_data"
        }

    return payload

def getCommoditySoup(startDate, endDate, dataFreq, commodityName, headers):
    print("COMMODITY SOUP")
    reqCommData = requests.post("https://www.investing.com/instruments/HistoricalDataAjax",
                             data=getPayload(startDate, endDate, dataFreq, commodityName),
                             headers=headers)
    commDataSoup = BeautifulSoup(reqCommData.text, 'html.parser')

    return commDataSoup

def getCommodityData(soup_data, commodityName):

    print("Commodity Data created")

    print(soup_data.prettify())

    listAllPrices = []
    for row in soup_data.find_all('td', class_="first left bold noWrap"):
        print("IN LOOP")
        date = row.get_text()
        price = str(row.find_next_sibling().get_text()).replace(",", "")

        priceSeries = pd.Series(data = price)
        priceSeries.name = date

        listAllPrices.append(priceSeries)
    
    oneCommDataDf = pd.concat(listAllPrices, axis = 0)
    oneCommDataDf.columns = [commodityName]
    # double check that index is dates

    print(oneCommDataDf)

    return oneCommDataDf

def main(source_filename, finaldata_filename):
    dataFull = pd.DataFrame() # set index as dates, columns as stocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }

    START_DATE = "07/03/2018"
    END_DATE = "07/03/2023"

    commColumns = []
    with open(source_filename) as f:
        for line in f.readlines():
            comm = line.strip()
            commColumns.append(comm)
            print(comm)

            commSoup = getCommoditySoup(START_DATE, END_DATE, "DAILY", comm, headers)
            oneDataDf = getCommodityData(commSoup, comm)

            dataFull = dataFull.join(oneDataDf)
    f.close()

    dataFull.columns = commColumns
    dataFull.to_csv(finaldata_filename)

    print("TO CSV")

main("commodities.txt", "commodities_data.csv")
