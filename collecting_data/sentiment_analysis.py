# Will write own Google News scraper at a later date <3

# Credits: https://towardsdatascience.com/stock-news-sentiment-analysis-with-python-193d4b4378d4

# Import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
from gnews import GNews

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
        dfHeadlines['date'] = pd.to_datetime(dfHeadlines.date, format="%b-%d-%y").dt.date

        return dfHeadlines
    else:
        return pd.DataFrame()

def scrapeFinViz(symb):
    symbURL = getFinURL(symb)
    symbSoup = getFinSoup(symbURL)
    symbAllHeadlines = getFinHeadlineTable(symbSoup, symb)

    return symbAllHeadlines


def scrapeGoogleNews(symb):
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
    vader = SentimentIntensityAnalyzer()

    scores = dfHeadlines['headline'].apply(vader.polarity_scores).tolist()
    scores_df = pd.DataFrame(scores)

    scores_headlines_df = pd.concat([dfHeadlines.reset_index(drop=True), scores_df.reset_index(drop=True)], axis=1)

    return scores_headlines_df

def getAverageScores(dfScoresAndHeadlines, stockSymb):
    dfScoresAndHeadlines = dfScoresAndHeadlines.drop(columns=["stocksymbol", "time", "headline"])

    df_Scores_Grouped_Mean = dfScoresAndHeadlines.groupby(['date']).mean().reset_index()

    df_Scores_Grouped_Mean.rename({col: stockSymb + "_" + col for col in df_Scores_Grouped_Mean.columns if col not in ['date']}, inplace = True)
   
    return df_Scores_Grouped_Mean


def main(source_filename):

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
                dfMeanScores.to_csv("sentiment_data/" + symb + "_sentiment.csv")

            print(".")

    f.close()

main("stocks.txt")
