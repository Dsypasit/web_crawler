import requests
from bs4 import BeautifulSoup
from Crawler import *

class Scrap:
    def __init__(self, url):
        self.url : str = url
        self.head = ['title']
        self.content = [['p']]
    
    def scrapping(self):
        res = requests.get(self.url)
        bs = BeautifulSoup(res.text, 'html.parser')
        head = self.head_scrapping(bs)
        content = self.content_scrapping(bs)
        return (head, content)

    def head_scrapping(self, bs):
        text = bs.find(*self.head).get_text()
        return text.strip()
    
    def content_scrapping(self, bs):
        text = []
        for pattern in self.content:
            text += bs.find_all(*pattern)
        text = " ".join(( t.get_text().strip() for t in text ))
        return text.strip()

class CNNScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)
        self.head = ['h1', {'class' : "pg-headline"}]
        self.content = [['div', {'class' : "zn-body__paragraph"}]]

class SkyScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def head_scrapping(self, bs):
        text = super().head_scrapping(bs).split('|')[0]
        return text

class BBCScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def head_scrapping(self, bs):
        text = super().head_scrapping(bs).split('-')[0]
        return text

class GoalScrap(Scrap):
    def __init__(self, url):
        super().__init__(url)

    def content_scrapping(self, bs):
        text = []
        for pattern in self.content:
            text += bs.find_all(*pattern)
        text = " ".join(( t.get_text().strip() for t in text[:-2] ))
        return text.strip()
    
    def head_scrapping(self, bs):
        text = super().head_scrapping(bs).split('|')[0]
        return text
        

if __name__ == "__main__":
    # crawler = GoalCrawler()
    # link = crawler.get_all_links()
    sc = BBCScrap('https://www.bbc.com/sport/football/60652298')
    sc.scrapping()
    print("-"*30)