import os
from pyparsing import Word
from Crawler import ExpressCrawler, Football365Crawler, GiveMeSportCrawler, IndianCrawler, KapookCrawler, KhaosodCrawler, NineZeroCrawler, SMMCrawler, SiamSportCrawler, SportBibleCrawler, SportMoleCrawler, SportingLifeCrawler, TPBSCrawler, TeamTalkCrawler, ThairathCrawler
from Scrap import ExpressScrap, Football365Scrap, GivemeScrap, GoalScrap, IndianScrap, KapookScrap, KhaosodScrap, NineZeroScrap, SiamScrap, SkyScrap, BBCScrap, CNNScrap, SmmScrap, SportBibleScrap, SportMoleScrap, SportingLifeScrap, TPBSScrap, TeamTalkScrap, ThairathScrap
from urllib.parse import urlparse
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
import re
import datetime
import time
from WordManager import WordManager
from CrawlerManager import CrawlerManager
from datetime import date

class ScrapManager:
    def __init__(self):
        self.links = None
        self.file = "all_url.csv"
        self.worker = 1000
        self.date_format = "%d/%m/%Y"
        self.lang = ['th', 'en', 'all']
        self.selected_lang = 'all'
        self.word_manager = WordManager()
        self.is_eng = lambda char: re.compile(r'[a-zA-Z]').match(char)

    def read_cached(self):
        d = pd.read_csv(self.file, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values
    
    def check_folder(self, folder):
        os.makedirs(folder, exist_ok=True)
    
    def save_data(self):
        path = 'data/'+str(date.today())+'/'
        self.check_folder('data')
        self.check_folder(path)
        df = self.url_data
        domains = df['domains'].unique().tolist()
        for domain in domains:
            data = df[df['domains'] == domain]
            filepath = path+'/'+domain+'/'
            self.check_folder(filepath)
            filename = filepath + 'data' + '.csv'
            data.to_csv(filename, index=False, encoding='utf-8')
        self.url_data.to_csv(path+'url_data.csv', index=False)
    
    def load_links(self, links=[]):
        if len(links):
            return links
        self.links = self.read_cached()
        return self.links
    
    def get_all_data(self, links=[]):
        links = self.load_links(links)
        self.url_data = pd.DataFrame({'date':[], 'ref':[], 'domains':[], 'url':[], 'header':[], 'content':[]}, dtype='str')
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor:
            results = (executor.submit(self.get_data, url) for url in links)
            for result in as_completed(results):
                re = result.result()
                if re:
                    self.url_data.loc[len(self.url_data.index)] = str(date.today()), *re
        self.url_data.drop(self.url_data[(self.url_data['header']=='') | (self.url_data['content']=='')].index, inplace=True)
        text_condition = lambda text: self.word_manager.clean_text(text) if self.is_eng(text.split()[0]) else self.word_manager.clean_text_th(text)
        self.url_data['header'] = self.url_data['header'].map(text_condition)
        self.url_data['content'] = self.url_data['content'].map(text_condition)
        return self.url_data.copy()

    def set_lang(self, lang):
        if lang in self.lang:
            self.selected_lang = lang

    def get_data(self, url):
        domain = self.url_domain(url)
        scrapper = None
        if domain in "https://www.goal.com/th":
            scrapper = GoalScrap(url)
        elif domain in "https://www.skysports.com/football":
            scrapper = SkyScrap(url)
        elif domain in "https://www.bbc.co.uk":
            scrapper = BBCScrap(url)
        elif domain in "https://edition.cnn.com/sport/football":
            scrapper = CNNScrap(url)
        elif domain in SiamSportCrawler().url:
            scrapper = SiamScrap(url)
        elif domain in NineZeroCrawler().url:
            scrapper = NineZeroScrap(url)
        elif domain in TeamTalkCrawler().url:
            scrapper = TeamTalkScrap(url)
        elif domain in Football365Crawler().url:
            scrapper = Football365Scrap(url)
        elif domain in ExpressCrawler().url:
            scrapper = ExpressScrap(url)
        elif domain in GiveMeSportCrawler().url:
            scrapper = GivemeScrap(url)
        elif domain in ThairathCrawler().url:
            scrapper = ThairathScrap(url)
        elif domain in SMMCrawler().url:
            scrapper = SmmScrap(url)
        elif domain in KapookCrawler().url:
            scrapper = KapookScrap(url)
        elif domain in SportMoleCrawler().url:
            scrapper = SportMoleScrap(url)
        elif domain in SportingLifeCrawler().url:
            scrapper = SportingLifeScrap(url)
        elif domain in IndianCrawler().url:
            scrapper = IndianScrap(url)
        elif domain in KhaosodCrawler().url:
            scrapper = KhaosodScrap(url)
        elif domain in TPBSCrawler().url:
            scrapper = TPBSScrap(url)
        elif domain in SportBibleCrawler().url:
            scrapper = SportBibleScrap(url)
        else:
            return
        data = scrapper.scrapping()
        return data
    
    def url_domain(self, url):
        url_parse = urlparse(url)
        return url_parse.scheme + "://" + url_parse.netloc

if __name__ == "__main__":
    craw = CrawlerManager()
    craw.get_all_links()
    manager = ScrapManager()
    start = time.time()
    data = manager.get_all_data()
    print(time.time() - start)
    manager.save_data()