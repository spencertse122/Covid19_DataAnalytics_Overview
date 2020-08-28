# Importing web connections libraries
import requests
import json
from datetime import datetime
import pandas as pd

# Main API connection, include storing required info, function to call for data
class ConnectAPI(object):
    def __init__(self, key):
        self.key = key

    def LoadingData(self, ticker, FullHistory=False):
        """
        Function to request the data from the Alphavantage Stock data API, return json data file
        """
        if FullHistory == False:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&apikey={}"
        else:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&outputsize=full&apikey={}"

        try:
            response = requests.get(url.format(ticker, self.key))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        # The API returns 200 status even after you have a typo
        try:
            outputjson = response.json()['Time Series (Daily)']
        except:
            print("Please check ticker for typos or mismatches")
            outputjson = None

        return outputjson, ticker


# Formatting data
class DataHandle(object):
    def __init__(self):
        pass

    def DataTrimmer(datatuple):
        """
        Simple cleanup tool to change the shape of the API return, and return a Pandas Series
        """
        TickerName = datatuple[1]

        df = pd.DataFrame(datatuple[0]).transpose()
        df.index = pd.DatetimeIndex(df.index)
        df = df[df.index >= datetime(2020,1,1)] # used 1/1/2020 because first Covid19 case in the US happened on 1/20/2020
        df = df.sort_index()
        df = df.rename(columns={"4. close":TickerName})

        outputseries = df[TickerName].astype(float)

        return outputseries

    def CombineSeries(*args):
        """
        Combining all the series into a dataframe
        """
        df = pd.concat([*args], axis=1)

        return df

    def GetSQL(df, table, OutputLocation):
        """
        Forming sql file to INSERT data
        """
        insert_query = "INSERT INTO {table} (DATE, SPY, GLD) VALUES ('{date}', '{stock1}', '{stock2}');"


        queries = []
        for index, row in df.iterrows():
            date = index.strftime("%Y-%m-%d")
            stock1 = row[0]
            stock2 = row[1]
            queries.append(insert_query.format(table=table, date=date, stock1=stock1, stock2=stock2))

        with open(OutputLocation+"/"+datetime.now().strftime("%Y%m%d")+"_FinanceMarketInsert.sql", "w") as output:
            output.write("\n".join(queries))



if __name__ == "__main__":
    tempkey = input("Please Enter API Key: ")
    StockToLook1 = ("Type in the first Stock ticker (e.g. TSLA): ")
    StockToLook2 = ("Type in the second Stockerticker (e.g. AAPL): ")

    testObject = ConnectAPI(key=tempkey)

    ob1 = DataHandle.DataTrimmer(testObject.LoadingData(StockToLook1, FullHistory=True))
    ob2 = DataHandle.DataTrimmer(testObject.LoadingData(StockToLook2, FullHistory=True))

    com = DataHandle.CombineSeries(ob1, ob2)

    DataHandle.GetSQL(com, "FinanceMarket", "SQLinsert")
