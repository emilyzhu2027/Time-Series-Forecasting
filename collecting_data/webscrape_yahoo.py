"""
Emily Zhu
Time Series Forecasting Project
Description: This file webscrapes Yahoo Finance to get daily stock and currency closing prices
from Jul 3 2018 - Jul 3 2023. The webscraped data are put into csv files in the 'webscraped_data' folder.
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
    """
    Parameters: 
        symb (str), stock ticker or currency symbol
        urlpt1 (str), the first part of the url before the passed symbol 
        urlpt2 (str), the second part of the url following the passed symbol

    Function:
        Combines multiple strings to create the url unique to each stock

    Return Val: 
        url (str), full url unique to one stock
    """

    url = urlpt1 + symb + urlpt2

    return url

def getSoup(url):
    """
    Parameters: 
        url (str), the url unique to one stock

    Function:
        Get the HTML code from the passed url by scrolling until the page no longer loads

    Return Val: 
        soupURL (bs4 object), the Beautiful Soup object of the passed web page
    """

    # Will open a Chrome window
    driver = webdriver.Chrome()
    driver.get(url)

    # Test to see if the table containing the historical data is present
    try:
        element_present = EC.presence_of_element_located((By.ID, 'Col1-1-HistoricalDataTable-Proxy')) 
        WebDriverWait(driver, 10).until(element_present)
    except TimeoutException:
        # This will occur if the historical data page isn't found
        print("Timed out waiting for page to load")
        return nan

    # Get height of screen to know how much to scroll in order to load new data
    SCREEN_HEIGHT = driver.execute_script("return window.screen.height;")

    # When to time out and leave the page - scrolling through the whole webpage should take under a minute
    timeout = time.time() + 60

    i = 1
    while True:
        # If the last date in the time frame I selected is on screen
        if (len(driver.find_elements(By.XPATH, "//span[text()='Jul 03, 2018']"))!=0):
            break
        else:
            # If the web scraper has been scrolling for over a minute - used to exit out of pages where the data wasn't collected in Jul 3 2018
            if (time.time() > timeout):
                break
            else:
                driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=SCREEN_HEIGHT, i=i))
                i += 1

    soupURL = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    return soupURL


def getTableRows(soupURL):
    """
    Parameters: 
        soupURL (bs4 object), the Beautiful Soup object of a web page

    Function:
        Retrieves the rows containing the data for each day

    Return Val: 
        tableRows (list of bs4 objects), list of all the BeautifulSoup objects which each represent a 
        row of data that contains one day's Open, High, Low, Close, Adj Close, and Volume
    """

    dataTable = soupURL.find("table", attrs={"data-test": "historical-prices"})
    dataTableBody = dataTable.find("tbody")
    tableRows = dataTableBody.find_all("tr")

    return tableRows

def getDatePriceSeries(soupRow):
    """
    Parameters: 
        soupRow (bs4 object - tr), one tr object containing a row of data for one day

    Function:
        Extracts the date and closing price from each row

    Return Val: 
        pd.Series() (empty Pandas Series), indicates that there is no closing price
        nan (nan), indicates that there is no date

        priceSeries (Pandas Series), contains the closing price for one day
        date (str), the date associated with the closing price
    """

    rowValues = soupRow.find_all("td")

    # If there's no closing price
    if (len(rowValues) < 4) or (len(rowValues[3].find_all("span")) == 0):
        print("Row doesn't have expected number of values")
        return pd.Series(), nan

    else:
        date = rowValues[0].find("span").get_text()
        closingPrice = rowValues[3].find("span").get_text()
        priceSeries = pd.Series(data = closingPrice)

        return priceSeries, date


def getOneSymbData(symb, symbURL):
    """
    Parameters: 
        symb (str), the stock ticker or currency symbol used by Yahoo Finance
        symbURL (str), the url associated with the passed symbol

    Function:
        Retrieves the closing prices and associated dates from Yahoo for the stock or currency symbol passed

    Return Val: 
        onePgDataDf (Pandas DataFrame), all the closing prices and dates from Jul 3 2018 to Jul 3 2023 of the 
        symbol passed
    """

    soupURL = getSoup(symbURL)

    # If no web page was found
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
    """
    Parameters: 
        source_filename (str), name of the file containing all the acronyms/symbols for the stocks and currencies
        whose data is being collected
        urlpt1 (str), first part of the universal url for historical data that goes before the symbol
        urlpt2 (str), second part of the universal url for historical data that goes after the symbol

    Function:
        Collects closing price data for all stocks/currencies in source file

    Return Val: 
        None
    """

    symbColumns = []
    with open(source_filename) as f:
        for line in f.readlines():
            symb = line.strip()
            symbColumns.append(symb)
            symbURL = getURL(symb, urlpt1, urlpt2)

            symbDataDF = getOneSymbData(symb, symbURL)

            finalcsvname = symb + "_data.csv"
            symbDataDF.to_csv("webscraped_data/" + finalcsvname)

    f.close()

# For stock tickers
main("stocks.txt", "https://finance.yahoo.com/quote/", "/history?period1=1530576000&period2=1688438445&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true")
# For currency acronyms
main("currencies.txt", "https://finance.yahoo.com/quote/", "%3DX/history?period1=1530576000&period2=1688342400&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true")
