from ast import keyword
import pandas as pd
import os
import re
from urllib.parse import urlparse
from Sentiment import Sentiment
import langdetect
import concurrent.futures
from concurrent.futures import as_completed
import time
from WordManager import WordManager
import random
from collections import Counter

class KeywordManager:

    def __init__(self):
        self.directory = 'web_keywords'
        self.filename = 'url_data.csv'
        self._columns=[
            'Link',
            'Keyword', 
            'Count',
            'Ref', 
            'Sentiment',
            'Language',
            'Domain',
            'Date']
        self.data = pd.DataFrame(columns=self._columns)
        self.csv_options =  {}
        self.sentiment = Sentiment()
        

        self.check_folder(self.directory)
        self.load_data()

    def check_folder(self, folder):
        os.makedirs(folder, exist_ok=True)
    
    def load_data(self):
        self.data_raw = pd.DataFrame(columns=['date', 'ref', 'domains', 'url', 'header', 'content'])
        data_path = f"data/"
        date_folder = [name for name in os.listdir(data_path) if os.path.isdir(data_path+name)]
        for d in date_folder:
            df = pd.read_csv(f"{data_path}/{d}/url_data.csv")
            self.data_raw = pd.concat([self.data_raw, df])
        self.data_raw.drop_duplicates(subset=['url', 'domains'])
        self.data_raw.dropna(inplace=True)
        return self.data_raw

    def n_gram_count(self, word, *contents):
        content = " ".join(contents)
        content = content.lower()
        reg = re.compile(r'[a-zA-Z]')
        word = word.lower()
        if reg.match(word):
            return content.count(word)
        else:
            return len(re.findall(word, content))
    
    def get_domain(self, keyword):
        path = self.directory+'/'+ keyword
        keywords = [name for name in os.listdir(path) if os.path.isdir(path+'/'+name)]
        return keywords

    def get_all_keywords(self):
        keywords = [name for name in os.listdir(self.directory) if os.path.isdir(self.directory+'/'+name)]
        return keywords

    def search_keyword(self, keyword, progress=None):
        keywords = self.get_all_keywords()
        if keyword in keywords and os.path.exists(self.directory+'/'+keyword+'/'+keyword+'.csv'):
            self.keyword_data = pd.read_csv(self.directory+'/'+keyword+'/'+keyword+'.csv')
            if progress != None:
                progress.emit(90)
        else:
            self.keyword_data = self.new_keyword_data(keyword, progress)
        return self.keyword_data
    
    def get_counter_word(self, keyword):
        self.count_data = pd.read_csv(self.directory+'/'+keyword+'/'+keyword+'_counter'+'.csv')
        return self.count_data

    
    def separated_domain(self, df, keyword):
        domains = df['Domain'].unique().tolist()
        for domain in domains:
            path = f'{self.directory}/{keyword}/{domain}/'
            data = df[df['Domain'] == domain]
            self.check_folder(path)
            filename = path + keyword + '.csv'
            data.to_csv(filename, index=False, encoding='utf-8')
    
    def _get_row_data(self, data):
        keyword, row = data
        count = self.n_gram_count(keyword, row['content'])
        if count<=1:
            return
        link = row['url']
        domain = urlparse(row['url']).netloc
        sentiment = self.sentiment.checksentimentword(" ".join([row['header'], row['content']]))
        lang = self.check_lang(row['header'])
        date = row['date']
        ref = row['ref']
        counter = self.count_word(row['content'], lang)
        return [link, keyword, count, ref, sentiment, lang, domain, date], counter
    
    def new_keyword_data(self, keyword, progress=None):
        data = pd.DataFrame(columns=self._columns)
        self.check_folder(f'{self.directory}/{keyword}')
        count = 0
        word_counter = Counter()
        with concurrent.futures.ThreadPoolExecutor(1000) as exercutor:
            results = (exercutor.submit(self._get_row_data, (keyword, row)) for index, row in self.data_raw.iterrows())
            for result in as_completed(results):
                row_data = result.result()
                if progress != None:
                    progress.emit(count/len(self.data_raw)*80)
                    count += 1
                if row_data != None:
                    row_data, counter = row_data
                    data.loc[len(data)] = row_data
                    word_counter += counter
        word_data = pd.DataFrame(word_counter.most_common(50), columns=['Words', 'Count'])
        data = data.sort_values(by=['Count', 'Ref'], ascending=False)
        self.separated_domain(data, keyword)
        data.to_csv(f'{self.directory}/{keyword}/{keyword}.csv', index=False, encoding='utf-8')
        word_data.to_csv(f'{self.directory}/{keyword}/{keyword}_counter.csv', index=False, encoding='utf-8')
        return data
    
    def check_lang(self, text):
        pattern = re.compile(r"[\u0E00-\u0E7F]")
        if len(re.findall(pattern, text)) > 0:
            return 'th'
        else:
            return 'en'
    
    def keywords_information(self):
        keywords = self.get_all_keywords()
        col = [
            'keywords',
            'Count',
            'Positive',
            'Negative',
            'Neatral'
        ]
        data = pd.DataFrame(columns=col)
        for keyword in keywords:
            keyword_data = self.search_keyword(keyword)
            count = keyword_data['Count'].sum()
            sentiment = keyword_data['Sentiment'].value_counts()
            positive = int(sentiment.get(['positive'], default=0))
            negative = int(sentiment.get(['negative'], default=0))
            neatral = int(sentiment.get(['neatral'], default=0))
            data.loc[len(data)] = (keyword, count, positive, negative, neatral)
        data.to_csv(self.directory+'/keywords.csv', index=False)
        return data

    def count_word(self, content, lang):
        word_manager = WordManager()
        if lang == 'th':
            return word_manager.counter_th(content)
        else:
            return word_manager.counter(content)

    
    def filter_domain(self, keyword, *domains):
        data = pd.DataFrame(columns=self._columns)
        path = f"{self.directory}/{keyword}"
        for d in domains:
            df = pd.read_csv(f"{path}/{d}/{keyword}.csv")
            data = pd.concat([data, df])
        data = data.sort_values(by=['Count', 'Ref'], ascending=False)
        return data

from time import time

if __name__ == "__main__":
    k = KeywordManager()
    start = time()
    # data = k.data_raw
    data = k.search_keyword('chelsea')
    data = k.search_keyword('arsenal')
    data = k.search_keyword('liverpool')
    data = k.search_keyword('แมนยู')
    data = k.search_keyword('โรนัลโด้')
    data = k.search_keyword('เมสซี่')
    print(time()-start)
    # print(k.get_all_keywords())
    # data = k.keywords_information()
    print(data)
        