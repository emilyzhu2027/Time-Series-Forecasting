# Pull news headlines about Nike - everyday from july 3 2018 to july 3 2023
# Run sentiment analysis - collect neg, neu, pos scores for each headline
# take average for each score for each day
# combine sentiment with scraped stock + currency data 
# combine with downlaoded other data

# Import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd

# USING NLTK FOR SENTIMENT ANALYSIS
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def getURL(symb):
    finwiz_urlPt1 = 'https://finviz.com/quote.ashx?t='

    return finwiz_urlPt1 + str(symb)

def getSoup(url):
    headerUser = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'}
    resp = requests.get(url, headers=headerUser)
    commDataSoup = BeautifulSoup(resp.text, 'html.parser')

    return commDataSoup

def getHeadlineTable(soup, symb):
    newsTable = soup.find(id='news-table')
    rows = newsTable.findAll("tr")

    listDataRows = []
    for i, table_row in enumerate(rows):
        headline = table_row.a.text
        date_time = table_row.td.text.split()

        date = date_time[0]
        time = date_time[1]

        listDataRows.append([symb, date, time, headline])
    
    dfHeadlines = pd.DataFrame(listDataRows, columns = ['stocksymbol', 'date', 'time', 'headline'])

    return dfHeadlines

def getSentimentScores(dfHeadlines):
    vader = SentimentIntensityAnalyzer()

    scores = dfHeadlines['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)

    scores_headlines_df = pd.concat([dfHeadlines, scores_df], axis=1)

    return scores_headlines_df

def getAverageScores(dfScoresAndHeadlines):
    df_Scores_Grouped_Mean = dfScoresAndHeadlines.groupby(['stocksymbol','date']).mean()
    df_Scores_Grouped_Mean = df_Scores_Grouped_Mean.unstack()
    df_Scores_Grouped_Mean = df_Scores_Grouped_Mean.xs('compound', axis=1).transpose()

    return df_Scores_Grouped_Mean


def main(source_filename, finaldata_filename):
    dataFull = pd.DataFrame() # set index as dates, columns as stocks

    with open(source_filename) as f:
        for line in f.readlines():
            symb = line.strip()
            symbURL = getURL(symb)
            symbSoup = getSoup(symbURL)
            symbAllHeadlines = getHeadlineTable(symbSoup, symb)
            symbScoresHeadlines = getSentimentScores(symbAllHeadlines)
            
            dfMeanScores = getAverageScores(symbScoresHeadlines)

    f.close()

    dfMeanScores.to_csv(finaldata_filename)

main("stocks.txt", "stock_sentiments.csv")




        

        


