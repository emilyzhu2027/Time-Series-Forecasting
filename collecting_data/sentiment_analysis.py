"""
Emily Zhu
Time Series Forecasting Project
Description: This file webscrapes FinWiz and Google News to get headlines on stocks
from Jul 3 2018 - Jul 3 2023. The sentiment scores for the scraped headlines for each stock are put into csv files within the
'sentiment_data' folder
Credits: https://towardsdatascience.com/stock-news-sentiment-analysis-with-python-193d4b4378d4
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
# Importing gnews library which will webscrape Google News 
from gnews import GNews

# Importing nltk for sentiment analysis
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def getFinURL(symb):
    """
    Parameters: 
        symb (str), stock ticker

    Function:
        Combines strings to create the FinWiz site url unique to each stock

    Return Val: 
        url (str), full FinWiz url for one stock

    """
    finwiz_urlPt1 = 'https://finviz.com/quote.ashx?t='

    return finwiz_urlPt1 + str(symb)

def getFinSoup(url):
    """
    Parameters: 
        url (str), FinWiz url for one stock

    Function:
        Gets the BeautifulSoup HTML for the FinWiz url

    Return Val: 
        dataSoup (bs4 object), BeautifulSoup object for the url passed containing the HTML for the web page
    """

    # Identifier for who's using the web page - so code doesn't get blocked by website
    headerUser = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'}
    resp = requests.get(url, headers=headerUser)
    dataSoup = BeautifulSoup(resp.text, 'html.parser')

    return dataSoup

def getFinHeadlineTable(soup, symb):
    """
    Parameters: 
        soup (bs4 object), BeautifulSoup for the FinWiz page associated with the stock ticker passed as symb
        symb (str), stock ticker

    Function:
        Gets the data from the table from the FinWiz site that contains all the recent headlines

    Return Val: 
        dfHeadlines (Pandas DataFrame), contains the stock ticker, date of the headline, time of the headline, and the headline itself
        pd.DataFrame() (Pandas DataFrame), empty DataFrame if no headlines are found
    """

    newsTable = soup.findAll(id='news-table')

    if len(newsTable) != 0:
        rows = newsTable[0].findAll("tr")

        listDataRows = []
        for i, table_row in enumerate(rows):

            headlineA = table_row.find_all("a")
            date_timeTD = table_row.find_all("td")

            if (len(headlineA) != 0):
                headline = headlineA[0].text
                date_time = date_timeTD[0].text.split()


                if len(date_time) != 1:
                    date = date_time[0]
                    time = date_time[1]
                else:
                    time = date_time[0]

                listDataRows.append([symb, date, time, headline])
            else:
                continue

        dfHeadlines = pd.DataFrame(listDataRows, columns = ['stocksymbol', 'date', 'time', 'headline'])
        dfHeadlines['date'] = pd.to_datetime(dfHeadlines.date, format="%b-%d-%y").dt.date

        return dfHeadlines
    else:
        return pd.DataFrame()

def scrapeFinWiz(symb):
    """
    Parameters: 
        symb (str), stock ticker

    Function:
        Gets the headlines from FinWiz for a certain stock ticker

    Return Val: 
        symbAllHeadlines (Pandas DataFrame), contains the stock ticker, date of the headline, time of the headline, and the headline itself 
    """

    symbURL = getFinURL(symb)
    symbSoup = getFinSoup(symbURL)
    symbAllHeadlines = getFinHeadlineTable(symbSoup, symb)

    return symbAllHeadlines


def scrapeGoogleNews(symb):
    """
    Parameters: 
        symb (str), stock ticker

    Function:
        Gets the headlines from Google News for a certain stock ticker within the time frame of July 3 2018 to July 3 2023

    Return Val: 
        news_Df (Pandas DataFrame), contains the stock ticker, date of the headline, and the headline itself 
    """

    # Opening a GNews object - to scrape google news within a specific time frame
    google_news = GNews(language='en', start_date=(2018, 7, 3), end_date=(2023, 7, 3))
    symb_news = google_news.get_news(symb + " news")

    news_Df = pd.DataFrame(symb_news)

    news_Df = news_Df.drop(columns = ["publisher", "description", "url"])
    news_Df.rename(columns={'title': 'headline', 'published date': 'raw_date'}, inplace = True)

    rawDateData = news_Df["raw_date"].str.split(" ", n = 1, expand = True)
    news_Df['date_time'] = rawDateData[1]

    news_Df['date'] = news_Df['date_time'].astype(str).str[0:11]
    news_Df['time'] = news_Df['date_time'].astype(str).str[12:]


    news_Df['date'] = pd.to_datetime(news_Df['date'], format = "%d %b %Y").dt.date

    news_Df = news_Df.drop(columns = ["raw_date", "date_time"])

    news_Df["stocksymbol"] = symb

    return news_Df

def getSentimentScores(dfHeadlines):
    """
    Parameters: 
        dfHeadlines (Pandas DataFrame), contains all dates and headlines for a stock

    Function:
        Gets the sentiment scores associated with each headline

    Return Val: 
        scoresHeadlinesDf (Pandas DataFrame), contains sentiment scores (positive, negative, neutral, and composite) 
        associated with all headlines and their respective dates
    """

    vader = SentimentIntensityAnalyzer()

    scores = dfHeadlines['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)

    scoresHeadlinesDf = pd.concat([dfHeadlines.reset_index(drop=True), scores_df.reset_index(drop=True)], axis=1)

    return scoresHeadlinesDf

def getAverageScores(dfScoresAndHeadlines, stockSymb):
    """
    Parameters: 
        dfScoresAndHeadlines (Pandas DataFrame), contains sentiment scores associated with all headlines and respective 
        dates for a stock
        stockSymb (Pandas DataFrame), stock ticker

    Function:
        Gets the average sentiment score of the headlines for each day available 

    Return Val: 
        scoresHeadlinesDf (Pandas DataFrame), contains sentiment scores (positive, negative, neutral, and composite) 
        associated with all headlines and their respective dates
    """

    dfScoresAndHeadlines = dfScoresAndHeadlines.drop(columns=["stocksymbol", "time", "headline"])

    df_Scores_Grouped_Mean = dfScoresAndHeadlines.groupby(['date']).mean().reset_index()

    df_Scores_Grouped_Mean.rename({col: stockSymb + "_" + col for col in df_Scores_Grouped_Mean.columns if col not in ['date']}, inplace = True)
   
    return df_Scores_Grouped_Mean

def main(source_filename):
    """
    Parameters: 
        source_filename (str), name of file that contains all the stock tickers for the stocks being used in 
        the analysis

    Function:
        Gets the sentiment scores for the dates where headlines are available for all stocks passed in the file 

    Return Val: 
        None
    """

    with open(source_filename) as f:
        for line in f.readlines():
            symb = line.strip()

            finAllHeadlines = scrapeFinWiz(symb)
            googleAllHeadlines = scrapeGoogleNews(symb)

            symbAllHeadlines = pd.concat([finAllHeadlines, googleAllHeadlines], axis = 0)

            if symbAllHeadlines.empty:
                continue
            else:
                symbScoresHeadlines = getSentimentScores(symbAllHeadlines)

                dfMeanScores = getAverageScores(symbScoresHeadlines, symb)
                dfMeanScores.to_csv("sentiment_data/" + symb + "_sentiment.csv")

    f.close()

main("stocks.txt")
