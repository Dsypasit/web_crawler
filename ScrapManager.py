from Scrap import GoalCrawler, GoalScrap, SkyScrap, BBCScrap, CNNScrap
from urllib.parse import urlparse
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed

class ScrapManager:
    def __init__(self):
        self.links = None
        self.file = "all_url.csv"
        self.worker = 1000
        self.data = pd.DataFrame({'url':[], 'header':[], 'content':[]}, dtype='str')
        self.lang = ['th', 'en', 'all']
        self.selected_lang = 'en'

    def read_cached(self):
        d = pd.read_csv(self.file, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values
    
    def save_data(self):
        self.data.to_csv('data.csv', index=False)
    
    def load_links(self, links=[]):
        if len(links):
            return links
        self.links = self.read_cached()
        return self.links
    
    def get_all_data(self, links=[]):
        links = self.load_links(links)
        self.data = pd.DataFrame({'url':[], 'header':[], 'content':[]}, dtype='str')
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor:
            results = (executor.submit(self.get_data, url) for url in links)
            for result in as_completed(results):
                re = result.result()
                if re:
                    self.data.loc[len(self.data.index)] = re
        return self.data.copy()

    def set_lang(self, lang):
        if lang in self.lang:
            self.selected_lang = lang

    def get_data(self, url):
        domain = self.url_domain(url)
        if self.selected_lang in ['th', 'all']:
            if domain in "https://www.goal.com/th":
                scrapper = GoalScrap(url)
            else: return
        if self.selected_lang in ['en', 'all']:
            if domain in "https://www.skysports.com/football":
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
    data = manager.get_all_data()
    manager.save_data()
    print(data[:20])