"""
Emily Zhu
7.3.23
Project #1: Predicting Nike Stocks
Description: This file webscrapes Yahoo Finance to get stock and currency data from Jul 3 2018 - Jul 3 2023 (once a day)
"""

from cmath import nan
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import time

def getURL(symb, urlpt1, urlpt2):
    url = urlpt1 + symb + urlpt2

    return url

def getSoup(url):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        element_present = EC.presence_of_element_located((By.ID, 'Col1-1-HistoricalDataTable-Proxy'))
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
        return nan

    SCREEN_HEIGHT = driver.execute_script("return window.screen.height;")

    timeout = time.time() + 60

    i = 1
    while True:
        if (len(driver.find_elements(By.XPATH, "//span[text()='Jul 03, 2018']"))!=0):
            print("BREAK!1")
            break
        else:
            if (time.time() > timeout):
                print("BREAK!2")
                break
            else:
                driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=SCREEN_HEIGHT, i=i)) 
                i += 1

        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=SCREEN_HEIGHT, i=i))
        i += 1

    
    soupURL = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    return soupURL


def getTableRows(soupURL):
    dataTable = soupURL.find("table", attrs={"data-test": "historical-prices"})
    dataTableBody = dataTable.find("tbody")
    tableRows = dataTableBody.find_all("tr")

    return tableRows

def getDatePriceSeries(soupRow):
    rowValues = soupRow.find_all("td")

    if (len(rowValues) < 4) or (len(rowValues[3].find_all("span")) == 0):
        print("Row doesn't have expected number of values")
        return pd.Series(), nan

    else:
        date = rowValues[0].find("span").get_text()
        closingPrice = rowValues[3].find("span").get_text()
        priceSeries = pd.Series(data = closingPrice)

        return priceSeries, date


def getOneSymbData(symb, symbURL):
    soupURL = getSoup(symbURL)

    if str(soupURL) == 'nan':
        return pd.DataFrame()

    symbRows = getTableRows(soupURL)

    listPriceSeries = []
    listDates = []
    for r in symbRows:
        priceSeries, date = getDatePriceSeries(r)
        listPriceSeries.append(priceSeries)

        if str(date) != 'nan':
            listDates.append(datetime.strptime(date, "%b %d, %Y"))

    onePgDataS = pd.concat(listPriceSeries, axis = 0)
    onePgDataS.index = listDates

    onePgDataDf = onePgDataS.to_frame()
    onePgDataDf.columns = [symb]

    return onePgDataDf


def main(source_filename, urlpt1, urlpt2):
    print(".")

    symbColumns = []
    with open(source_filename) as f:
        for line in f.readlines():
            symb = line.strip()
            print(symb)
            symbColumns.append(symb)
            symbURL = getURL(symb, urlpt1, urlpt2)

            symbDataDF = getOneSymbData(symb, symbURL)
            print(symbDataDF)

            finalcsvname = symb + "_data.csv"
            symbDataDF.to_csv("webscraped_data/" + finalcsvname)

    f.close()

main("stocks.txt", "https://finance.yahoo.com/quote/", "/history?period1=1530576000&period2=1688438445&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true")
main("currencies.txt", "https://finance.yahoo.com/quote/", "%3DX/history?period1=1530576000&period2=1688342400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true")
