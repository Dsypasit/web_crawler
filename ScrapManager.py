from pyparsing import Word
from Scrap import GoalCrawler, GoalScrap, SkyScrap, BBCScrap, CNNScrap
from urllib.parse import urlparse
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
import re
import datetime
import time
from WordManager import WordManager
from CrawlerManager import CrawlerManager

class ScrapManager:
    def __init__(self):
        self.links = None
        self.file = "all_url.csv"
        self.worker = 1000
        self.url_data = pd.DataFrame({'url':[], 'header':[], 'content':[]}, dtype='str')
        self.date_format = "%d/%m/%Y"
        self.lang = ['th', 'en', 'all']
        self.selected_lang = 'all'
        self.keywords_data = pd.DataFrame({'keywords':pd.Series(dtype='str'), 'count':pd.Series(dtype='int'), 'date':pd.Series(dtype='str'), 'lang':pd.Series(dtype='str')})
        self.keywords = ['chelsea', 'ronaldo', 'arsenal', 'liverpool']
        self.word_manager = WordManager()
        self.is_eng = lambda char: re.compile(r'[a-zA-Z]').match(char)
        self.load_keywords_data()

    def read_cached(self):
        d = pd.read_csv(self.file, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values
    
    def load_keywords_data(self):
        try:
            self.keywords_data = pd.read_csv('keywords_data.csv', index_col=False)
            self.keywords = self.keywords_data['keywords'].unique().tolist()
        except pd.errors.EmptyDataError:
            self.keywords_data = pd.DataFrame({'keywords':pd.Series(dtype='str'), 'count':pd.Series(dtype='int'), 'date':pd.Series(dtype='str'), 'lang':pd.Series(dtype='str')})
            self.keywords = ['chelsea', 'ronaldo', 'arsenal', 'liverpool']
    
    def append_keywords(self, word):
        self.keywords.append(word)
        self.keywords = list(set(self.keywords))
                
    def save_keywords_data(self):
        try:
            old_keyword = pd.read_csv('keywords_data.csv')
            data = pd.concat([old_keyword, self.keywords_data]).drop_duplicates(['keywords', 'date'], keep='last')
            data.sort_values(by="date", key=lambda i:pd.to_datetime(i, format=self.date_format), inplace=True)
            data.to_csv('keywords_data.csv', index=False)
        except pd.errors.EmptyDataError:
            self.keywords_data.to_csv('keywords_data.csv', index=False)
    
    def save_data(self):
        self.url_data.to_csv('url_data.csv', index=False)
        self.save_keywords_data()
    
    def load_links(self, links=[]):
        if len(links):
            return links
        self.links = self.read_cached()
        return self.links
    
    def get_all_data(self, links=[]):
        links = self.load_links(links)
        self.url_data = pd.DataFrame({'url':[], 'header':[], 'content':[]}, dtype='str')
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor:
            results = (executor.submit(self.get_data, url) for url in links)
            for result in as_completed(results):
                re = result.result()
                if re:
                    self.url_data.loc[len(self.url_data.index)] = re
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
        if self.selected_lang in ['th', 'all']:
            if domain in "https://www.goal.com/th":
                scrapper = GoalScrap(url)
        if self.selected_lang in ['en', 'all']:
            if domain in "https://www.skysports.com/football":
                scrapper = SkyScrap(url)
            elif domain in "https://www.bbc.co.uk":
                scrapper = BBCScrap(url)
            elif domain in "https://edition.cnn.com/sport/football":
                scrapper = CNNScrap(url)
        if not scrapper:
            return
        data = scrapper.scrapping()
        return data
    
    def url_domain(self, url):
        url_parse = urlparse(url)
        return url_parse.scheme + "://" + url_parse.netloc
    
    def get_keywords_data(self):
        if len(self.url_data) == 0:
            self.get_all_data()
        self.keywords_data = pd.DataFrame({'keywords':pd.Series(dtype='str'), 'count':pd.Series(dtype='int'), 'date':pd.Series(dtype='str'), 'lang':pd.Series(dtype='str')})
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = ( executor.submit(self.keywords_processing, i) for i in self.keywords)
            for result in as_completed(results):
                result_data = result.result()
                self.keywords_data.loc[len(self.keywords_data.index)] = result_data
        return self.keywords_data.copy()
    
    def keywords_processing(self, word):
        start = time.time()
        count = 0
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor:
            results = (executor.submit(lambda contents: self.n_gram_count(word, *contents), contents) for contents in self.url_data.loc[:, ['header', 'content']].values)
            for result in as_completed(results):
                count += result.result()
        date = datetime.datetime.today().strftime(self.date_format)
        # date = datetime.datetime.today() + datetime.timedelta(days=1)
        # date = date.strftime(self.date_format)
        lang = 'eng' if self.is_eng(word) else 'th'
        print(word, time.time() - start)
        return word, count, date, lang

    def n_gram_count(self, word, *contents):
        content = " ".join(contents)
        reg = re.compile(r'[a-zA-Z]')
        if reg.match(word):
            return content.count(word)
        else:
            return len(re.findall(word, content))

if __name__ == "__main__":
    # craw = CrawlerManager()
    # craw.get_all_links()
    manager = ScrapManager()
    data = manager.get_all_data()
    # keyword_data = manager.get_keywords_data()
    # print(keyword_data)
    manager.append_keywords('ลิเวอร์พูล')
    keywords_data2 = manager.get_keywords_data()
    print(keywords_data2)
    manager.save_data()