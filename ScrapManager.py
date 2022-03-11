from Scrap import GoalCrawler, GoalScrap, SkyScrap, BBCScrap, CNNScrap
from urllib.parse import urlparse
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed

class ScrapManager:
    def __init__(self):
        self.links = None
        self.file = "all_url.csv"
        self.data = pd.DataFrame({'header':[], 'content':[]}, dtype='str')
        self.worker = 1000

    def read_cached(self):
        d = pd.read_csv(self.file, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values
    
    def save_data(self):
        self.data.to_csv('data.csv', index=False)
    
    def load_links(self, links=None):
        if links:
            self.links = links
            return
        self.links = self.read_cached()
    
    def get_all_scrap(self, links=None):
        self.load_links(links)
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor:
            results = (executor.submit(self.get_data, url) for url in self.links)
            for result in as_completed(results):
                re = result.result()
                if re:
                    self.data.loc[len(self.data.index)] = re
        return self.data.copy()


    def get_data(self, url):
        domain = self.url_domain(url)
        if domain in "https://www.goal.com/th":
            scrapper = GoalScrap(url)
        elif domain in "https://www.skysports.com/football":
            scrapper = SkyScrap(url)
        elif domain in "https://www.bbc.co.uk":
            scrapper = BBCScrap(url)
        elif domain in "https://edition.cnn.com/sport/football":
            scrapper = CNNScrap(url)
        else:
            return
        data = scrapper.scrapping()
        return data
    
    def url_domain(self, url):
        url_parse = urlparse(url)
        return url_parse.scheme + "://" + url_parse.netloc

if __name__ == "__main__":
    manager = ScrapManager()
    data = manager.get_all_scrap()
    manager.save_data()
    print(data[:20])