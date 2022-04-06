import pandas as pd
import os
import re
from urllib.parse import urlparse

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
            'Domain']
        self.data = pd.DataFrame(columns=self._columns)
        self.csv_options =  {}
        

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
    
    def separated_domain(self, df, keyword):
        domains = df['Domain'].unique().tolist()
        for domain in domains:
            path = f'{self.directory}/{keyword}/{domain}/'
            data = df[df['Domain'] == domain]
            self.check_folder(path)
            filename = path + keyword + '.csv'
            data.to_csv(filename, index=False, encoding='utf-8')
        
    
    def new_keyword(self, keyword):
        data = pd.DataFrame(columns=self._columns)
        self.check_folder(f'{self.directory}/{keyword}')
        for index, row in self.data_raw.iterrows():
            link = row['url']
            title = row['header']
            domain = urlparse(row['url']).netloc
            count = self.n_gram_count(keyword, row['content'], row['header'])
            data.loc[len(data)] = [link, title, keyword, count, 'Positive', domain]
        data = data.sort_values(by=['Count'], ascending=False)
        self.separated_domain(data, keyword)
        data.to_csv(f'{self.directory}/{keyword}/{keyword}.csv', index=False, encoding='utf-8')
        return data


if __name__ == "__main__":
    k = KeywordManager()
    data = k.new_keyword('chelsea')
    print(data.head())
        