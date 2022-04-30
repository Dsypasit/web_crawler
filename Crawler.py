import re
import requests
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
from urllib.parse import unquote, urlparse
import urllib.robotparser
from copy import deepcopy
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

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
        self.is_scroll = False
        self.is_clicked = False
        self.id_click = []
        self.by = None
        self.session()

    def read_robot(self, link):
        try:
            url_parse = urlparse(link)
            robot_link = url_parse.scheme+"://"+url_parse.netloc+"/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robot_link)
            rp.read()
            return rp
        except urllib.error.URLError:
            return False
    
    def session(self):
        self.s = requests.Session()
        self.s.max_redirects = 30

    def get_url_content(self, link):
        if not self.check_url(link):
            return
        if self.rp != False:
            if not self.rp.can_fetch("*", link):
                return
        try:
            r = self.s.get(link, timeout=3)
            # r = requests.get(link, timeout=3)
            r.encoding = 'utf-8'    # set encoding
            html_text = r.text
            return html_text
        except :
            pass

    def filter_links(self, links=[]):
        """ Filter links"""
        # if self._before_filter_links is None: return []
        if len(links)>0:
            url_parse = urlparse(self.url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            links = [i for i in links if i]    # concate url and /abc/def (route)
            links = [raw_url+i if (i[0] == '/') else i for i in links]    # concate url and /abc/def (route)
            return links
        elif len(self._before_filter_links) == 0:
            return links
        if self.no_domain and len(self._before_filter_links) > 0 :
            url_parse = urlparse(self.url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            self._before_filter_links = [i for i in self._before_filter_links if i]    # concate url and /abc/def (route)
            self._before_filter_links = [raw_url+i if (i[0] == '/') else i for i in self._before_filter_links]    # concate url and /abc/def (route)
        fil_links = list(filter(self.regex.match, self._before_filter_links))
        return fil_links.copy()

    def get_url_links(self, content):
        if not content: return []
        url_reg2 = re.compile(r"href='(.*?)'")  # select string in href
        url_reg3 = re.compile(r'href="(.*?)"')
        result = re.findall(url_reg2, content)
        result += re.findall(url_reg3, content)
        result = [i.strip() for i in result.copy() if i]
        return deepcopy(result)

    def get_sublink(self, s_url):
        if self.rp != False:
            if self.rp.can_fetch("*", s_url):
                content = self.get_url_content(s_url)
                sub = self.get_url_links(content)
                return sub.copy()
            else:
                return 
        content = self.get_url_content(s_url)
        sub = self.get_url_links(content)
        return sub.copy()

    def get_all_links(self):
        start = time.time()
        url = self.url
        self.rp = self.read_robot(url)
        self._before_filter_links = []
        if self.is_scroll == True:
            content = self.scroll_down(url)
            sub_l = self.get_url_links(content)
        elif self.is_clicked == True:
            content = self.click_button(url)
            sub_l = self.get_url_links(content)
        else:
            sub_l = self.get_sublink(url)
        # sub_l = self.filter_links(links=sub_l)
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
        print(url, "success", time.time()-start)
        return self.links['url'].values

    def check_url(self, url):
        url_parse = urlparse(url)
        return all([url_parse.scheme, url_parse.netloc])
    
    def scroll_down(self, url):
        path = 'webdriver/'
        # os.chdir(path)
        driver = webdriver.Chrome(path+"chromedriver.exe")
        driver.get(url)
        SCROLL_PAUSE_TIME = 0.5
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight")
        c = 0
        while c<6:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            c += 1
        html = driver.page_source
        return html
    
    def click_button(self, url):
        path = 'webdriver/'
        # os.chdir(path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(path+"chromedriver.exe", chrome_options=chrome_options)
        driver.get(url)
        SCROLL_PAUSE_TIME = 1
        c = 0
        while c<6:
            try:
                driver.find_element(self.by, ' '.join(self.id_click)).click()
                time.sleep(SCROLL_PAUSE_TIME)
                c+= 1
            except:
                break
        html = driver.page_source
        return html


class GoalCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.goal.com/th"
        self.no_domain = True
    
    def filter_links(self, links=[]):
        if len(links)>0:
            url_parse = urlparse(self.url)
            raw_url = url_parse.scheme + "://" + url_parse.netloc
            links = [i for i in links if i]    # concate url and /abc/def (route)
            links = [raw_url+i if (i[0] == '/') else i for i in links]    # concate url and /abc/def (route)
            return links
        elif len(self._before_filter_links) == 0:
            return links
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

class NineZeroCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.90min.com/"
        self.regex = re.compile(r'(https\:\/\/www\.90min\.com\/posts\/.*)')

class TeamTalkCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.teamtalk.com"
        self.regex = re.compile(r'(https\:\/\/www\.teamtalk\.com\/news\/.*)')

class ExpressCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.express.co.uk/sport/football/"
        self.regex = re.compile(r'(https\:\/\/www\.express\..*\/sport\/football\/\d{7}\/.*)')
        self.no_domain = True

class Football365Crawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.football366.com/"
        self.regex = re.compile(r'(https\:\/\/www\.football365\.com\/news\/.*)')

class GiveMeSportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.givemesport.com/"
        self.regex = re.compile(r'(https\:\/\/www\.givemesport\.com\/\d{8}.*)')

class ThairathCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.thairath.co.th/sport/eurofootball"
        self.regex = re.compile(r'(https\:\/\/www\.thairath\..*\/sport\/.*\/\d{7})')
        self.no_domain = True

class SMMCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.smmsport.com/football/international/"
        self.regex = re.compile(r'(https\:\/\/www\.smmsport\..*\/reader\/news\/.*)')

class KapookCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://football.kapook.com/newslist"
        self.regex = re.compile(r'(https\:\/\/football\.kapook\..*\/news-\d{5})')

class SportMoleCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.sportsmole.co.uk/"
        self.regex = re.compile(r'(https\:\/\/www\.sportsmole\..*_\d{6}.html)')
        self.no_domain = True
       
class SportingLifeCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.sportinglife.com/football/news"
        self.regex = re.compile(r'(https\:\/\/www\.sportinglife\.com\/football\/news\/.*\d{6})')
        self.no_domain = True

class DailyRecordCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.dailyrecord.co.uk/sport/football/football-news/"
        self.regex = re.compile(r'(https\:\/\/www\.dailyrecord\.co.uk\/sport\/football\/.*)')

class IndianCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://indianexpress.com/section/sports/football/"
        self.regex = re.compile(r'(https\:\/\/indianexpress.com\/article\/sports\/football\/.*-\d{7})')

class KhaosodCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.khaosod.co.th/%E0%B8%9A%E0%B8%AD%E0%B8%A5%E0%B9%82%E0%B8%A5%E0%B8%81/worldcup-news"
        self.regex = re.compile(r'(https\:\/\/www\.khaosod\..*\/news_\d{7})')

class TPBSCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://news.thaipbs.or.th/search?q=%E0%B8%9F%E0%B8%B8%E0%B8%95%E0%B8%9A%E0%B8%AD%E0%B8%A5%E0%B9%82%E0%B8%A5%E0%B8%81"
        self.regex = re.compile(r'(https\:\/\/news\.thaipbs\..*\/\d{5,})')

class SportBibleCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.sportbible.com/football"
        self.regex = re.compile(r'(https\:\/\/www\.sportbible.com\/football\/.*\d{6,})')
        self.no_domain = True

class EspnCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://global.espn.com/football/"
        self.regex = re.compile(r'(https\:\/\/global.espn.com\/football\/*)')
        self.no_domain = True
        self.is_scroll = True

class NdtvCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://sports.ndtv.com/football/news"
        self.regex = re.compile(r'(https\:\/\/sports.ndtv.com\/football\/*)')
        self.no_domain = True
        self.is_clicked = True
        self.by = By.ID
        self.id_click = ['loadmorebtn']

class SuperSportCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://supersport.com/football/news/"
        self.regex = re.compile(r'(https\:\/\/supersport.com\/football\/*)')
        self.no_domain = True
        self.is_clicked = True
        self.by = By.CLASS_NAME
        self.id_click = ['button-load-more']

class CollegeCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://collegefootballnews.com/"
        self.regex = re.compile(r'(https\:\/\/collegefootballnews.com\/list\/*)')
        self.is_scroll = True

class CbssCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.cbssports.com/nfl/"
        self.regex = re.compile(r'(https\:\/\/www.cbssports.com\/nfl\/news\/*)')
        self.no_domain = True
        self.is_clicked = True
        self.by = By.CLASS_NAME
        self.id_click = ['button-type-lines ']
        


if __name__ == "__main__":
    def time_spent(func, *args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(time.time()-start)
        return result
    pd.options.display.max_colwidth = 600
    # crawler = DailyRecordCrawler()
    # crawler = CollegeCrawler()
    crawler = CbssCrawler()
    data = time_spent(crawler.get_all_links)
    print(data[:21])
    print(len(data))
    # for i in data[:21]:
    #     s = SportingLifeScrap(i)
    #     a = s.scrapping()
    #     print(a)