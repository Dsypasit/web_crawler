import re
import requests
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
from urllib.parse import unquote, urlparse
import urllib.robotparser
from copy import deepcopy
from time import time
import numpy as np

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

    def read_robot(self, link):
        url_parse = urlparse(link)
        robot_link = url_parse.scheme+"://"+url_parse.netloc+"/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robot_link)
        rp.read()
        return rp

    def get_url_content(self, link):
        if not self.check_url(link):
            return
        if not self.rp.can_fetch("*", link):
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
        # if self._before_filter_links is None: return []
        if self.no_domain and len(self._before_filter_links) > 0 :
            url_parse = urlparse(self.url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            self._before_filter_links = [i for i in self._before_filter_links if i]    # concate url and /abc/def (route)
            self._before_filter_links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]    # concate url and /abc/def (route)
        fil_links = list(filter(self.regex.match, self._before_filter_links))
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

    def get_sublink(self, s_url):
        if self.rp.can_fetch("*", s_url):
            content = self.get_url_content(s_url)
            sub = self.get_url_links(content)
            return sub.copy()

    def get_all_links(self):
        start = time()
        url = self.url
        self.rp = self.read_robot(url)
        self._before_filter_links = []
        sub_l = self.get_sublink(url)
        count = 5
        while sub_l == [] and count > 0:
            sub_l = self.get_sublink(url)
            count -= 1
        self._before_filter_links += sub_l.copy()
        self._before_filter_links = pd.Series(self._before_filter_links).drop_duplicates()
        if self.no_domain:
            url_parse = urlparse(url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            self._before_filter_links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]  # concate url and /abc/def (route)
        with concurrent.futures.ThreadPoolExecutor(self.worker) as executor :
            results = [executor.submit(self.get_sublink, i) for i in self._before_filter_links[1:]]
            for result in as_completed(results):
                self._before_filter_links = np.append(self._before_filter_links, result.result())
        self._before_filter_links = self.filter_links()
        self.links = pd.DataFrame({'url':self._before_filter_links})
        self.links.drop_duplicates(subset=['url'], inplace=True)
        print(url, "success", time()-start)
        return self.links['url'].values

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
        r = re.compile(r"(https:\/\/www\.goal\.com\/th\/(ข่าว|ลิสต์)\/)(?!\d).*")
        fil_links = list(filter(r.match, links_edit))
        return fil_links.copy()

class SkySportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.skysports.com/football"
        self.regex = re.compile(r"https:\/\/www\.skysports\.com\/football\/(news|story-telling)\/.*")
    
class SiamSportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.siamsport.co.th/football/international"
        self.regex = re.compile(r"https:\/\/www\.siamsport\.co\.th\/football\/.*\/view\/.*")

class CNNCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://edition.cnn.com/sport/football"
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

def time_spent(func, *args, **kwargs):
    start = time()
    result = func(*args, **kwargs)
    print(time()-start)
    return result


if __name__ == "__main__":
    pd.options.display.max_colwidth = 600
    crawler = SkySportCrawler()
    data = time_spent(crawler.get_all_links)
    print(data[:20])