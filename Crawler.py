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
        self.url : str = ""
        self.word : str = ""
        self.worker : int = 1000
        self.links : pd.core.frame.DataFrame = None
        self.no_domain : bool = False
        self.regex = ""
        self.regex = re.compile("")
        self._before_filter_links : list = []

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

    def filter_links(self):
        """ Filter links"""
        if self.no_domain:
            url_parse = urlparse(self.url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            self._before_filter_links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]    # concate url and /abc/def (route)
        fil_links = list(filter(self.regex.match, self._before_filter_links))
        self.links = pd.DataFrame({'url':fil_links})
        return fil_links.copy()

    def n_gram_count(self, content):
        """ Count word in content"""
        return content.count(self.word)

    def get_url_links(self, content):
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
        sub = self.get_url_links(content)
        return sub.copy()

    def get_all_links(self):
        url = self.url
        self._before_filter_links = [url]
        sub_l = self.get_sublink(url)
        count = 5
        while sub_l == [] and count > 0:
            sub_l = self.get_sublink(url)
            count -= 1
        self._before_filter_links += sub_l.copy()
        if self.no_domain:
            url_parse = urlparse(url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            self._before_filter_links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]  # concate url and /abc/def (route)
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = [executor.submit(self.get_sublink, i) for i in self._before_filter_links[1:]]
            for result in as_completed(results):
                self._before_filter_links += result.result()
        self._before_filter_links = self.filter_links()
        self.write_url(self._before_filter_links.copy())
        self.links = pd.DataFrame({'url':self._before_filter_links})
        print("")
        return deepcopy(self._before_filter_links)

    def add_n_gram(self, url):
        con = self.get_url_content(url)
        if con == None:
            return (url, 0)
        n = self.n_gram_count(con)
        return (url, n)

    def set_word(self, word):
        self.word = word
    
    def check_url(self, url):
        url_parse = urlparse(url)
        return all([url_parse.scheme, url_parse.netloc])

class GoalCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.goal.com/th"
        self.no_domain = True
    
    def filter_links(self):
        url_parse = urlparse(self.url)
        raw_url = url_parse.scheme + "://" + url_parse.netloc
        links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]    # concate url and /abc/def (route)
        links_edit = [unquote(i) for i in links]    #   change %E%0%9 (url encode) to thai lang
        r = re.compile(r"https:\/\/www\.goal\.com\/th\/(ข่าว|ลิสต์)\/.*")
        fil_links = list(filter(r.match, links_edit))
        self.links = pd.DataFrame({'url':fil_links})
        return fil_links.copy()

class SkySportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.skysports.com/football"
        self.regex = re.compile(r"https:\/\/www\.skysports\.com\/football\/(news|story-telling)\/.*")
    
class SiamSportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.goal.com/th"
        self.regex = re.compile(r"https:\/\/www\.siamsport\.co\.th\/football\/.*\/view\/.*")

class CNNCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.goal.com/th"
        self.regex = re.compile(r'https\:\/\/edition\.cnn\.com\/\d{4}\/\d{2}\/\d{2}\/football\/.*')
        self.no_domain = True
    
class BBCCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.bbc.com/sport/football"
        self.regex = re.compile(r"https:\/\/www\.bbc\..*\/sport\/football\/\d+")
        
class SoccerSuckCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.soccersuck.com"
        self.regex = re.compile(r"https:\/\/www\.soccersuck\.com\/boards\/topic\/.*")

class DailyMailCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.dailymail.co.uk/sport/football"
        self.regex = re.compile(r'((https\:\/\/www\.dailymail\..*\/sport\/football\/article-\d+\/.*\.html)(?!#))')

class CrawlerManager():
    def __init__(self):
        self.worker = 1000
        self.links = ["https://www.goal.com/th", "https://www.skysports.com/football", "https://www.siamsport.co.th/football/international", "https://www.soccersuck.com", 
        "https://www.bbc.com/sport/football", "https://www.dailymail.co.uk/sport/football", "https://edition.cnn.com/sport/football"]
        self.all_links = None
        self.data = pd.DataFrame({'url':[], 'n_gram':[]})

    def get_links_multithread(self):
        with open("all_url.csv", 'w', encoding="utf-8") as f :
            f.write("url\n")
        all_links = []
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = (executor.submit(self.get_links, link) for link in self.links)
            for result in as_completed(results):
                all_links += result.result()
        self.all_links = pd.Series(all_links)
        self.all_links.drop_duplicates(inplace=True)
        return self.all_links.copy()

    def get_n_gram_multithread(self, word):
        if len(self.all_links) == 0:
            self.all_links = self.get_pd('all_url.csv')
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

class Crawler_test:
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
    # crawler = Crawler()

    # time_spent(crawler.get_links_multithread)
    # crawler.set_word('Messi')
    # data = time_spent(crawler.get_n_gram_multithread)
    # print(data[:20])
    # print(len(crawler.fil_links))

    manager = CrawlerManager()
    data = manager.get_links_multithread()
    print(len(data))
    data2 = manager.get_n_gram_multithread("Russia")
    print(data2[:20])