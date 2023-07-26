### Project Title: Time Series Prediction of Nike Stock Direction

#### General Description:
This project attempts to use a LSTM recurrent neural network to predict the direction of Nike stocks from the closing prices of other related stocks, commodity prices, currency prices, and sentiment scores of headlines surrounding stocks. The data was collected by scraping Yahoo Finance, Google News, and FinWiz. The data is then imputed and scaled before being used to train a RNN to predict the direction of Nike stock closing prices.
#### Description of Files:
* collecting_data/currencies.txt: list of selected currency acronyms used by Yahoo Finance
* collecting_data/stocks.txt: list of selected stock stickers used by Yahoo Finance
* collecting_data/webscrape_yahoo.py: scrapes Yahoo Finance for currency and stock data, creates csv files in 'webscraped_data' directory
* collecting_data/sentiment_analysis.py: scrapes Google News and FinWiz for stock headlines, calculates sentiment scores for stock headlines, creates csv files in 'sentiment_data' directory
* collecting_data/webscraped_data: contains csv files of scraped stock and currency closing price data
* collecting_data/downloaded_data: contains csv files of commodity price data that were downloaded manually
* collecting_data/sentiment_data: contains csv files of sentiment scores scraped and calculated sentiment scores for stocks
* collecting_data/combining_data.py: combines all data files into one, creates 'full_data.csv'
* collecting_data/full_data.csv: full collected data
* neuralnetwork.py: scales and imputes data, trains and tests the LSTM RNN
#### Project Status:
I've completed collecting data. And now, I'm currently working on coding and testing the neural network to optimize it.
#### Usage:
##### To begin with collecting data --
* Download combining_data.py, sentiment_analysis.py, webscrape_yahoo.py, stocks.txt, currencies.txt
* Install the following libraries: Pandas, Numpy, Selenium, Chromdriver, GNews, Requests, bs4
* Run webscrape_yahoo.py, sentiment_analysis.py
* Download commodity price data from Investing.com
* Run combining_data.py
* Run neuralnetwork.py

#### Relevant Links:
* https://towardsdatascience.com/web-scraping-for-accounting-analysis-using-python-part-1-b5fc016a1c9a
* https://www.geeksforgeeks.org/web-scraping-financial-news-using-python/
* https://medium.com/analytics-vidhya/using-python-and-selenium-to-scrape-infinite-scroll-web-pages-825d12c24ec7
* https://machinelearningmastery.com/using-cnn-for-financial-time-series-prediction/
* https://towardsdatascience.com/recurrent-neural-networks-by-example-in-python-ffd204f99470
* https://christianmartinezfinancialfox.medium.com/learning-python-for-finance-how-to-get-started-with-advanced-financial-forecasting-in-python-43553dac9d69
* https://towardsdatascience.com/lstm-recurrent-neural-networks-how-to-teach-a-network-to-remember-the-past-55e54c2ff22e
