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

class KeywordManager:

    def __init__(self):
        self.directory = 'web_keywords'
        self.filename = 'url_data.csv'
        self._columns=[
            'Link',
            'Title',
            'Keyword', 
            'Count', 
            'Sentiment',
            'Language',
            'Domain']
        self.data = pd.DataFrame(columns=self._columns)
        self.csv_options =  {}
        self.sentiment = Sentiment()
        

        self.check_folder(self.directory)
        self.load_data()

    def check_folder(self, folder):
        os.makedirs(folder, exist_ok=True)
    
    def load_data(self):
        self.data_raw = pd.read_csv(self.filename)
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
        keywords = [name for name in os.listdir(self.directory)]
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
        link = row['url']
        title = row['header']
        domain = urlparse(row['url']).netloc
        sentiment = self.sentiment.checksentimentword(" ".join([row['header'], row['content']]))
        lang = self.check_lang(title)
        count = self.n_gram_count(keyword, row['content'], row['header'])
        if count>0:
            return [link, title, keyword, count, sentiment, lang, domain]
        else:
            return None
    
    def new_keyword_data(self, keyword, progress=None):
        data = pd.DataFrame(columns=self._columns)
        self.check_folder(f'{self.directory}/{keyword}')
        count = 0
        with concurrent.futures.ThreadPoolExecutor(1000) as exercutor:
            results = (exercutor.submit(self._get_row_data, (keyword, row)) for index, row in self.data_raw.iterrows())
            for result in as_completed(results):
                row_data = result.result()
                if progress != None:
                    progress.emit(count/len(self.data_raw)*80)
                    count += 1
                if row_data != None:
                    data.loc[len(data)] = row_data
        data = data.sort_values(by=['Count'], ascending=False)
        self.separated_domain(data, keyword)
        data.to_csv(f'{self.directory}/{keyword}/{keyword}.csv', index=False, encoding='utf-8')
        return data
    
    def check_lang(self, text):
        pattern = re.compile(r"[\u0E00-\u0E7F]")
        if len(re.findall(pattern, text)) > 0:
            return 'th'
        else:
            return 'en'
    
    def filter_domain(self, keyword, *domains):
        data = pd.DataFrame(columns=self._columns)
        path = f"{self.directory}/{keyword}"
        for d in domains:
            df = pd.read_csv(f"{path}/{d}/{keyword}.csv")
            data = pd.concat([data, df])
        data = data.sort_values(by=['Count'], ascending=False)
        return data


if __name__ == "__main__":
    k = KeywordManager()
    data = k.search_keyword('chelsea')
    data = k.search_keyword('arsenal')
    data = k.search_keyword('liverpool')
    data = k.search_keyword('แมนยู')
    data = k.search_keyword('โรนัลโด้')
    data = k.search_keyword('เมสซี่')
    # print(k.get_all_keywords())
    # data = k.get_domain('ar')
    print(data)
        