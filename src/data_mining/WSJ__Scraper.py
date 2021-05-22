import requests 
from bs4 import BeautifulSoup
import pandas as pd



class WSJ__Scraper:
    """Useful for income statements"""
    def __init__(self):
        self.baseUrl = "https://www.wsj.com"
        
    
    def __createDataframeFromIncomeStatementTable(self, table):
        rows = table.findAll("tr")
        dates = [ str(el).strip("<th>").strip("</th>") for el in table.findAll("th")[1:-1] ]    
        data = { "Dates": dates }
        for row in rows:
            tds = row.findAll("td")
            if len(tds) > 0 and tds[0].text != "":
                data[tds[0].text] = [ td.text for td in tds[1:len(dates)+1] ]
        df = pd.DataFrame(data)
        df = df.set_index("Dates")
        return df        
    
    
    def __parseIncomeStatementsFromHtml(self, html):
        """Parse the income statement table as a dataframe"""
        soup = BeautifulSoup(html, 'html.parser')
        incomeStatementTable = soup.findAll("table", { "class": "cr_dataTable" })[0]
        return self.__createDataframeFromIncomeStatementTable(incomeStatementTable)
    
        
    def __getIncomeStatements(self, ticker, period):
        """
        Get income statements from WSJ
        Period = [ 'quarter', 'annual' ]
        """
        url = f"{self.baseUrl}/market-data/quotes/{ticker}/financials/{period}/income-statement"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return self.__parseIncomeStatementsFromHtml(response.content)
        raise Exception(f"Bad request: status {response.status_code}")
        
        
    def getQuarterlyIncomeStatements(self, ticker):
        return self.__getIncomeStatements(ticker, "quarter")
    
    
    def getAnnualIncomeStatements(self, ticker):
        return self.__getIncomeStatements(ticker, "annual")
