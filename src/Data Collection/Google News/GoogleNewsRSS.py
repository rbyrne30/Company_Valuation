import requests
import feedparser

class GoogleNewsRSS(object):
    def __init__(self):
        self.rss = "https://news.google.com/rss"

    def search(self, query, intitle=None, startDate=None, endDate=None, timeFrame=None):
        url = self.rss + "/search?q=" + query
        
        if not startDate is None:
            url += f"+after:{startDate}"

        if not endDate is None:
            url += f"+before:{endDate}"

        if not timeFrame is None:
            url += f"+when:{timeFrame}"
        
        if not intitle is None:
            url += f"+allintitle:{intitle}"

        return self.rssParse(url)


    def rssParse(self, url):
        print(f"Getting data from {url}")
        return feedparser.parse(url)['entries']



if __name__ == "__main__":
    entries = GoogleNewsRSS().search("Apple", timeFrame="1d")
    
    for entry in entries:
        print(entry['title'])
        print(entry['published'])
        print(entry.keys())
        print("")
