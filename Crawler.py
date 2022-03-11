import re
import requests
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
import numpy as np
from urllib.parse import unquote, urlparse
from copy import deepcopy
from time import time

class Crawler:
    def __init__(self):
        self.word = ""
        self.links = ["https://www.goal.com/th", "https://www.skysports.com/football", "https://www.siamsport.co.th/football/international", "https://www.soccersuck.com", 
        "https://www.bbc.com/sport/football", "https://www.dailymail.co.uk/sport/football", "https://edition.cnn.com/sport/football"]
        self.fil_links = []
        self.worker = 1000

    def get_pd(self, filename):
        d = pd.read_csv(filename, index_col=False, on_bad_lines='skip') # import file and ignore bad line
        d = d.drop_duplicates(subset=['url'])   # drop duplicate
        return d['url'].values

    def get_url_content(self, link):
        if not self.check_url(link):
            return
        try:
            r = requests.get(link, timeout=3)
            r.encoding = 'utf-8'    # set encoding
            html_text = r.text
            return html_text
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.InvalidSchema):
            pass

    def filter_links(self, base_url, links):
        links = deepcopy(links)
        if base_url == "https://www.skysports.com/football":
            r = re.compile(r"https:\/\/www\.skysports\.com\/football\/(news|story-telling)\/.*")
            fil_links = list(filter(r.match, links))
            return fil_links.copy()
        elif base_url == "https://www.goal.com/th":
            url_parse = urlparse(base_url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            links = [raw_url+i if (i[0] == '/') else i for i in deepcopy(links)]    # concate url and /abc/def (route)
            links_edit = [unquote(i) for i in links]    #   change %E%0%9 (url encode) to thai lang
            r = re.compile(r"https:\/\/www\.goal\.com\/th\/(ข่าว|ลิสต์)\/.*")
            fil_links = list(filter(r.match, links_edit))
            return fil_links.copy()
        elif base_url == "https://www.siamsport.co.th/football/international":
            r = re.compile(r"https:\/\/www\.siamsport\.co\.th\/football\/.*\/view\/.*")
            fil_links = list(filter(r.match, links))
            return fil_links.copy()
        elif base_url == "https://www.soccersuck.com":
            r = re.compile(r"https:\/\/www\.soccersuck\.com\/boards\/topic\/.*")
            fil_links = list(filter(r.match, links))
            return fil_links.copy()
        elif base_url == "https://www.bbc.com/sport/football":
            r = re.compile(r"https:\/\/www\.bbc\..*\/sport\/football\/\d+")
            fil_links = list(filter(r.match, links))
            return fil_links.copy()
        elif base_url == "https://www.dailymail.co.uk/sport/football":
            r = re.compile(r'((https\:\/\/www\.dailymail\..*\/sport\/football\/article-\d+\/.*\.html)(?!#))')
            fil_links = list(filter(r.match, links))
            return fil_links.copy()
        elif base_url == "https://edition.cnn.com/sport/football":
            url_parse = urlparse(base_url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            links = [raw_url+i if (i[0] == '/') else i for i in links]  # concate url and /abc/def (route)
            r = re.compile(r'https\:\/\/edition\.cnn\.com\/\d{4}\/\d{2}\/\d{2}\/football\/.*')
            fil_links = list(filter(r.match, links)) # Read Note
            return fil_links.copy()
        else:
            return links

    def n_gram_count(self, content, word):
        return content.count(word)
        # return len(re.findall(word, content))

    def get_url_links(self, url, content):
        if not content: return []
        url_reg2 = re.compile(r"href='(.*?)'")  # select string in href
        url_reg3 = re.compile(r'href="(.*?)"')
        result = re.findall(url_reg2, content)
        result += re.findall(url_reg3, content)
        result = [i.strip() for i in result.copy() if i]
        return deepcopy(result)

    def write_url(self, l):
        with open("all_url.csv", 'r+', encoding='utf8') as f :
            f.readlines()   # cursor point at last line
            l = [i.strip()+"\n" for i in l]
            f.writelines(l)

    def get_sublink(self, s_url):
        content = self.get_url_content(s_url)
        sub = self.get_url_links(s_url, content)
        return sub.copy()

    def get_all_links(self, url):
        l = [url]
        sub_l = self.get_sublink(url)
        count = 5
        while sub_l == [] and count > 0:
            sub_l = self.get_sublink(url)
            count -= 1
        l += sub_l.copy()
        if url in ("https://www.goal.com/th", "https://edition.cnn.com/sport/football"):
            url_parse = urlparse(url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            l = [raw_url+i if (i[0] == '/') else i for i in l]  # concate url and /abc/def (route)
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = [executor.submit(self.get_sublink, i) for i in l[1:]]
            for result in as_completed(results):
                l += result.result()
        l = self.filter_links(url, l)
        self.write_url(l.copy())
        print(url,"success")
        return deepcopy(l)

    def add_n_gram(self, url, word):
        con = self.get_url_content(url)
        if con == None:
            return (url, 0)
        n = self.n_gram_count(con, word)
        return (url, n)

    def get_links_multithread(self):
        with open("all_url.csv", 'w', encoding="utf-8") as f :
            f.write("url\n")
        all_links = []
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = (executor.submit(self.get_all_links, link) for link in self.links)
            for result in as_completed(results):
                all_links += result.result()
        self.fil_links = pd.Series(all_links)
        self.fil_links.drop_duplicates(inplace=True)
        return self.fil_links.values

    def get_n_gram_multithread(self):
        if len(self.fil_links) == 0:
            self.fil_links = self.get_pd('all_url.csv')
        if self.word == "":
            return None
        self.data = pd.DataFrame({'url':[], 'n_gram':[]})
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = ( executor.submit(lambda url: self.add_n_gram(url, self.word), i) for i in self.fil_links)
            for result in as_completed(results):
                url, n = result.result()
                self.data.loc[len(self.data.index)] = [url, n]
        self.data = self.data.sort_values(by=['n_gram'], ascending=False)
        return self.data
    
    def set_word(self, word):
        self.word = word
    
    def check_url(self, url):
        url_parse = urlparse(url)
        return all([url_parse.scheme, url_parse.netloc])

def time_spent(func, *args, **kwargs):
    start = time()
    result = func(*args, **kwargs)
    print(time()-start)
    return result


if __name__ == "__main__":
    pd.options.display.max_colwidth = 600
    crawler = Crawler()

    time_spent(crawler.get_links_multithread)
    crawler.set_word('Messi')
    data = time_spent(crawler.get_n_gram_multithread)
    print(data[:20])
    print(len(crawler.fil_links))