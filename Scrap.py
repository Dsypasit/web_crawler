from ast import expr_context
import requests
from bs4 import BeautifulSoup
from Crawler import *

class Scrap:
    def __init__(self, url):
        self.url : str = url
        self.head = ['title']
        self.content = [['p']]
    
    def scrapping(self):
        try:
            res = requests.get(self.url, timeout=30)
        except:
            return None
        bs = BeautifulSoup(res.text, 'html.parser')
        head = self.head_scrapping(bs)
        content = self.content_scrapping(bs)
        return (self.url, head, content)

    def head_scrapping(self, bs):
        try:
            text = bs.find(*self.head).get_text()
            return text.strip()
        except:
            return "no header"
    
    def content_scrapping(self, bs):
        try:
            text = []
            for pattern in self.content:
                text += bs.find_all(*pattern)
            text = " ".join(( t.get_text().strip() for t in text ))
            return text.strip()
        except:
            return "no content"

class CNNScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class' : "pg-headline"}]
        self.content = [['div', {'class' : "zn-body__paragraph"}]]

class SkyScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def head_scrapping(self, bs):
        try:
            text = super().head_scrapping(bs).split('|')[0]
            return text
        except:
            return ""

class BBCScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def head_scrapping(self, bs):
        try:
            text = super().head_scrapping(bs).split('-')[0]
            return text
        except:
            return "no header"

class GoalScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def content_scrapping(self, bs):
        try:
            text = []
            for pattern in self.content:
                text += bs.find_all(*pattern)
            text = " ".join(( t.get_text().strip() for t in text[:-2] ))
            return text.strip()
        except:
            return "no content"
    
    def head_scrapping(self, bs):
        try:
            text = super().head_scrapping(bs).split('|')[0]
            return text
        except:
            return "no header"

class SiamScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class NineZeroScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class' : 'tagStyle_1l41t8p-o_O-title_1c5zcc4-o_O-sidesPadding_1kaga1a'}]

class TeamTalkScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class Football365Scrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class ExpressScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class GivemeScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class': 'gms-content-headline'}]

class ThairathScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class SmmScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class': 'article-title'}]

class KapookScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class SportMoleScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1']

class SportingLifeScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class':'Article__ArticleHeadline-wr9av4-2 fKQgEP'}]

class IndianScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class':'native_story_title'}]

class KhaosodScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class':'udsg__main-title'}]

class TPBSScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class':'content-title'}]

class SportBibleScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class':'css-1h8vhnh'}]


if __name__ == "__main__":
    # crawler = GoalCrawler()
    # link = crawler.get_all_links()
    sc = SportBibleScrap('https://www.sportbible.com/football/marcandre-ter-stegen-didnt-pick-lionel-messi-in-his-dream-xi-20220320')
    print(sc.scrapping())
    print("-"*30)