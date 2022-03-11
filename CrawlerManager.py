from Crawler import SiamSportCrawler, SkySportCrawler, GoalCrawler, CNNCrawler, BBCCrawler, SoccerSuckCrawler, DailyMailCrawler
import concurrent.futures
from concurrent.futures import as_completed
import pandas as pd
import numpy as np
import requests
pd.options.display.max_colwidth = 600

class CrawlerManager():
    def __init__(self):
        self.worker = 1000
        self.links = ["https://www.goal.com/th", "https://www.skysports.com/football", "https://www.siamsport.co.th/football/international", "https://www.soccersuck.com", 
        "https://www.bbc.com/sport/football", "https://www.dailymail.co.uk/sport/football", "https://edition.cnn.com/sport/football"]
        self.all_links = None
        self.data = pd.DataFrame({'url':[], 'n_gram':[]})
        self.file = "all_url.csv"

    def read_cached(self):
        d = pd.read_csv(self.file, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values
    
    def save_links(self):
        with open("all_url.csv", 'r+', encoding='utf8') as f :
            f.readline()
            l = [i.strip()+"\n" for i in self.all_links.values]
            f.writelines(l)

    def get_all_links(self, cached=False):
        if cached:
            self.all_links = self.read_cached()
            return self.all_links
        with open(self.file, 'w', encoding="utf-8") as f :
            f.write("url\n")
        all_links = np.array([])
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = (executor.submit(self.get_links, link) for link in self.links)
            for result in as_completed(results):
                all_links = np.append(all_links, result.result())
        self.all_links = pd.Series(all_links)
        self.save_links()
        return self.all_links.copy()

    def get_n_gram_data(self, word):
        if len(self.all_links) == 0:
            self.all_links = self.read_cached()
            return self.all_links
        if word == "":
            return None
        self.word = word
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = ( executor.submit(self.count_url_ngram, i) for i in self.all_links)
            for result in as_completed(results):
                url, n = result.result()
                self.data.loc[len(self.data.index)] = [url, n]
        self.data = self.data.sort_values(by=['n_gram'], ascending=False)
        return self.data.copy()

    def get_url_content(self, link):
        try:
            r = requests.get(link, timeout=3)
            r.encoding = 'utf-8'    # set encoding
            html_text = r.text
            return html_text
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema):
            pass

    def n_gram_count(self, content):
        return content.count(self.word)

    def count_url_ngram(self, url):
        con = self.get_url_content(url)
        if con == None:
            return (url, 0)
        n = self.n_gram_count(con)
        return (url, n)

    
    def get_links(self, url):
        crawler = self.create_crawler(url)
        links = crawler.get_all_links()
        return links
    
    def create_crawler(self, url):
        if url == "https://www.goal.com/th":
            crawler = GoalCrawler()
        elif url == "https://www.skysports.com/football":
            crawler = SkySportCrawler()
        elif url == "https://www.siamsport.co.th/football/international":
            crawler = SiamSportCrawler()
        elif url == "https://www.soccersuck.com":
            crawler = SoccerSuckCrawler()
        elif url == "https://www.bbc.com/sport/football":
            crawler = BBCCrawler()
        elif url == "https://www.dailymail.co.uk/sport/football":
            crawler = DailyMailCrawler()
        elif url == "https://edition.cnn.com/sport/football":
            crawler = CNNCrawler()
        else:
            return
        return crawler


from time import time
def time_spent(func, *args, **kwargs):
    start = time()
    result = func(*args, **kwargs)
    print(time()-start)
    return result

if __name__ == "__main__":
    manager = CrawlerManager()
    data = time_spent(manager.get_all_links)
    print(len(data))
    data2 = time_spent(manager.get_n_gram_data, "เมสซี")
    print(data2[:20])