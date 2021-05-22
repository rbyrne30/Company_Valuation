import config as cfg
import requests 
from bs4 import BeautifulSoup
import pandas as pd
import os
import random
import time

USER_AGENTS = cfg.user_agents
SAVE_FOLDER = cfg.datamining__saveFolder
SLEEP_MIN = 3
SLEEP_MAX = 10

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
DF_INDEX = "Date"


def getAllRatiosForTicker(ticker, useCache=True):
    """Fetches all ratios from https://www.macrotrends.net and stores 
    them as a dataframe
    
    data includes:
     - PE ratio
     - Price-Sales ratio
     - Price-Book ratio
     - Prce-FCF ratio
     - Current ratio
     - Quick ratio
     - Debt-Equity ratio
     - ROE (Return on Equity)
     - ROA (Return on Assets)
     - ROI (Return on Investment)
     - Return on Tangible Equity"""
     
    df = __getSavedRatios(ticker) if useCache else None
    if df is None:
        print(f"Ratios not previously saved for {ticker}. Fetching data...")
        df = __getAllRatios(ticker)
        print("Done")
    return df


def __getSavedRatios(ticker):
    """Gets saved data for ticker ratios if saved, else returns None"""
    dataPath = __fileNameForRatios(ticker)
    if os.path.exists(dataPath):
        return pd.read_csv(dataPath).set_index(DF_INDEX)
    return None


def __fileNameForRatios(ticker):
    """Returns the filename that should be used to store data for ticker"""
    return f"{SAVE_FOLDER}/{ticker}_ratios.csv"


def __randSleep():
    randSleep = random.randrange(SLEEP_MIN, SLEEP_MAX)
    print(f"Sleeping for {randSleep} seconds...")
    time.sleep(randSleep)


def __getAllRatios(ticker):
    """Fetches all ratio data for ticker"""
    baseUrl = __getBaseUrl(ticker)

    peRatio = __getPERatio(baseUrl, ticker)
    __randSleep()
    psRatio = __getPSRatio(baseUrl, ticker)
    __randSleep()
    pbRatio = __getPriceBookRatio(baseUrl, ticker)
    __randSleep()
    pfcfRatio = __getPriceFCFRatio(baseUrl, ticker)
    __randSleep()
    cRatio = __getCurrentRatio(baseUrl, ticker)
    __randSleep()
    qRatio = __getQuickRatio(baseUrl, ticker)
    __randSleep()
    deRatio = __getDebtEquityRatio(baseUrl, ticker)
    # roe = __getROE(baseUrl, ticker)
    # roa = __getROA(baseUrl, ticker)
    # roi = __getROI(baseUrl, ticker)
    # rote = __getReturnOnTangibleEquity(baseUrl, ticker)

    df = peRatio
    for df2 in [ psRatio, pbRatio, pfcfRatio, cRatio, qRatio, deRatio ]:
        df = df.join(df2, how="outer")
    df.to_csv(__fileNameForRatios(ticker))
    return df


def __getPERatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "pe-ratio")

def __getPSRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "price-sales")

def __getPriceBookRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "price-book")

def __getPriceFCFRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "price-fcf")

def __getCurrentRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "current-ratio")

def __getQuickRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "quick-ratio")

def __getDebtEquityRatio(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "debt-equity-ratio")

def __getROE(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "roe")

def __getROA(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "roa")

def __getROI(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "roi")

def __getReturnOnTangibleEquity(baseUrl, ticker):
    return __getTableData(baseUrl, ticker, "return-on-tangible-equity")


def __getBaseUrl(ticker):
    return requests.get(f"https://www.macrotrends.net/stocks/charts/{ticker}", headers=HEADERS).url

    
def __sendRequest(baseUrl, ticker, slug):
    url = baseUrl + slug 
    return requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})


def __parseDataTable(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findAll("div", { "id": "style-1" })[0].findAll("table")[0]
    labels = [ th.text for th in table.findAll("th") ][1:]
    rows = table.findAll("tr")[2:]
    data = []
    for row in rows:
        data.append([ td.text for td in row.findAll("td") ])
    df = pd.DataFrame(data, columns=labels).set_index("Date")
    if '%' in df.iloc[0][-1]:
        df.iloc[:,-1] = df.iloc[:,-1].str.strip("%").astype(float) / 100
    return df

def __getTableData(baseUrl, ticker, slug):
    html = __sendRequest(baseUrl, ticker, slug).content
    df = __parseDataTable(html)
    return pd.DataFrame(df.iloc[:,-1], index=df.index)



if __name__ == "__main__":
    print(getAllRatiosForTicker("MSFT", False))