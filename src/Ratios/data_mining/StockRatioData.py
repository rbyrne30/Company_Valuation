from data_mining import MacroTrends
import config as cfg
from datetime import datetime, timedelta
import pandas as pd
import os
import pandas_datareader.data as pdr 
import numpy as np

SAVE_FOLDER = cfg.datamining__saveFolder
TARGET_COL = "Share Price"



def getDifferenceFromAverageDataForTicker(ticker, sectorTickers, daysOffset, useCache=True):
    df = __getAllDataForTicker(ticker, daysOffset, useCache)
    avg_df = __getAverageDataForTickers(sectorTickers, daysOffset, useCache)
    dif_df = df.subtract(avg_df).div(avg_df).drop([
        "Return on Equity", "Return on Assets", "Return on Investment", "Return on Tangible Equity"
    ], axis=1)
    targetCol = np.array(df[TARGET_COL])
    returns = (targetCol[1:]-targetCol[:-1])/targetCol[:-1]
    returns = np.append(returns, np.nan)
    dif_df[TARGET_COL] = returns
    return dif_df
    


def getAllDataForTicker(ticker, sectorTickers, daysOffset, useCache=True):
    """Fetch all the available data for ticker
    data includes:
     - ratios 
     - share prices"""
    df = __getAllDataForTicker(ticker, daysOffset, useCache)
    avg_df = __getAverageDataForTickers(sectorTickers, daysOffset, useCache)
    avg_df.columns = [ f"Sector {colName}" for colName in avg_df.columns ]
    return df.join(avg_df, how="outer").drop(["Return on Equity", "Return on Assets", "Return on Investment", 
                    "Return on Tangible Equity", "Sector Return on Equity", "Sector Return on Assets", 
                    "Sector Return on Investment", "Sector Return on Tangible Equity", "Sector Share Price"], axis=1)
    


def __getAllDataForTicker(ticker, daysOffset, useCache):
    df = MacroTrends.getAllRatiosForTicker(ticker)

    startDate = df.index[0]
    endDate = df.index[-1] 
    fileName = __fileName(ticker, startDate, endDate, daysOffset)

    if useCache and os.path.exists(fileName):
        return pd.read_csv(fileName).set_index("Date")

    closingPrices = __getClosingPriceForDates(ticker, df.index, daysOffset)
    df[TARGET_COL] = closingPrices
    df.to_csv(fileName) 
    return df


def __getAverageDataForTickers(tickers, daysOffset, useCache):
    print(f"Gathering data for {tickers[0]}...")
    df = __getAllDataForTicker(tickers[0], daysOffset, useCache)
    for ticker in tickers:
        print(f"Gathering data for {ticker}...")
        ticker_df = __getAllDataForTicker(ticker, daysOffset, useCache)
        try:
            df = df.add(ticker_df.astype(float))
        except:
            print(ticker_df)
            raise
    return df.div(len(tickers))


def __getClosingPriceForDates(ticker, dates, daysOffset):
    datesOffset = [ datetime.strptime(date, "%Y-%m-%d")+timedelta(days=daysOffset) for date in dates ]
    datesOffset = [ date.strftime("%Y-%m-%d") for date in datesOffset if date < date.today() ]
    data = [ __getTickerData(ticker, date, None)["Close"].iloc[0] for date in datesOffset ]
    return pd.DataFrame(data, columns=[ticker], index=dates[-len(data):])


def __getTickerData(ticker, start, end):
    return pdr.DataReader(ticker, 'yahoo', start, end)


def __fileName(ticker, startDate, endDate, daysOffset):
    return f"{SAVE_FOLDER}/{ticker}_data_{startDate}--{endDate}--{daysOffset}_day_lag"



