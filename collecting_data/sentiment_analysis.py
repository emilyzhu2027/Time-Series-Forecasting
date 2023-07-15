# Will write own Google News scraper at a later date <3

# Import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd

# USING NLTK FOR SENTIMENT ANALYSIS
import nltk
nltk.downloader.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def getFinURL(symb):
    finwiz_urlPt1 = 'https://finviz.com/quote.ashx?t='

    return finwiz_urlPt1 + str(symb)

def getFinSoup(url):
    headerUser = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36'}
    resp = requests.get(url, headers=headerUser)
    commDataSoup = BeautifulSoup(resp.text, 'html.parser')

    return commDataSoup

def getFinHeadlineTable(soup, symb):
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

        return dfHeadlines
    else:
        return pd.DataFrame()

def scrapeFinViz(symb):
    symbURL = getFinURL(symb)
    symbSoup = getFinSoup(symbURL)
    symbAllHeadlines = getFinHeadlineTable(symbSoup, symb)

    return symbAllHeadlines


def scrapeGoogleNews(symb):
    url = "https://www.google.com/search?q=nike+stock&tbs=cdr:1,cd_min:7/3/2018,cd_max:7/3/2023,sbd:1&tbm=nws&num=300"
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')




def getSentimentScores(dfHeadlines):
    vader = SentimentIntensityAnalyzer()

    scores = dfHeadlines['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)

    scores_headlines_df = pd.concat([dfHeadlines, scores_df], axis=1)

    return scores_headlines_df

def getAverageScores(dfScoresAndHeadlines, stockSymb):
    dfScoresAndHeadlines = dfScoresAndHeadlines.drop(columns=["stocksymbol", "time", "headline"])

    df_Scores_Grouped_Mean = dfScoresAndHeadlines.groupby(['date']).mean().reset_index()
    df_Scores_Grouped_Mean = df_Scores_Grouped_Mean.add_prefix(stockSymb + "_")

    return df_Scores_Grouped_Mean


def main(source_filename, finaldata_filename):
    dataFull = pd.DataFrame() # set index as dates, columns as stocks

    with open(source_filename) as f:
        for line in f.readlines():
            symb = line.strip()
            finAllHeadlines = scrapeFinViz(symb)
            googleAllHeadlines = scrapeGoogleNews(symb)

            symbAllHeadlines = pd.concat([finAllHeadlines, googleAllHeadlines], axis = 0)

            if symbAllHeadlines.empty:
                continue
            else:
                symbScoresHeadlines = getSentimentScores(symbAllHeadlines)
                
                dfMeanScores = getAverageScores(symbScoresHeadlines, symb)

                dataFull = pd.concat([dataFull, dfMeanScores], axis = 1)
           

    f.close()


    dataFull.to_csv(finaldata_filename)

main("stocks.txt", "stock_sentiments.csv")




        

        


