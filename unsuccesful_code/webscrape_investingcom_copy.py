import requests
from bs4 import BeautifulSoup
import urllib
import pandas as pd
from random import randint
from requests.structures import CaseInsensitiveDict

def getURL(startDateCode, endDateCode, commodityName):
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

    # fixed numbers: current time, fixed parameters, D: daily
    url = "https://tvc4.investing.com/0e818888003657176127862245791911/1664515691/56/56/23/history?symbol=101810&resolution=D&from=1633411692&to=1664515752"

    return url

def getSoup(url, headers):
    resp = requests.get(url, headers=headers)
    print(resp.status_code)
    commDataSoup = BeautifulSoup(resp.text, 'html.parser')

    return commDataSoup

def getHeaders():
    print("GET HEADERS")
    # pulled from investing.com - api calls when changing date
    

    headers = CaseInsensitiveDict()
    headers["authority"] = "tvc4.investing.com"
    headers["accept"] = "*/*"
    headers["accept-language"] = "en-US,en;q=0.9"
    headers["content-type"] = "text/plain"
    headers["origin"] = "https://tvc-invdn-com.investing.com"
    headers["referer"] = "https://tvc-invdn-com.investing.com/"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-site"
    headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36"

    return headers

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

    START_DATE_CODE = 1530641060 #07/03/2018
    END_DATE_CODE = 1688407460 #07/03/2023

    commColumns = []
    with open(source_filename) as f:
        for line in f.readlines():
            comm = line.strip()
            commColumns.append(comm)
            
            commURL = getURL(START_DATE_CODE, END_DATE_CODE, comm)
            headers = getHeaders()

            commSoup = getSoup(commURL, headers)

            # MORE SHIT

            dataFull = dataFull.join(oneDataDf)
    f.close()

    dataFull.columns = commColumns
    dataFull.to_csv(finaldata_filename)

    print("TO CSV")

main("commodities.txt", "commodities_data.csv")
