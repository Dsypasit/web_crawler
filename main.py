import time
from urllib.request import urlopen
import re
import requests
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
import numpy as np
from urllib.parse import unquote, urlparse
from copy import deepcopy
from collections import Counter

def get_pd(filename):
    d = pd.read_csv(filename, index_col=False, on_bad_lines='skip')
    d = d.drop_duplicates(subset=['url'])
    return d['url'].values

def get_url_content(link):
    try:
        r = requests.get(link, timeout=3)
        r.encoding = 'utf-8'
        html_text = r.text
        return html_text
    except :
        pass

def filter_links(base_url, links):
    links = deepcopy(links)
    if base_url == "https://www.skysports.com/football":
        r = re.compile(r"https:\/\/www\.skysports\.com\/football\/(news|story-telling)\/.*")
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    elif base_url == "https://www.goal.com/th":
        url_parse = urlparse(base_url)
        raw_url = url_parse.scheme + "://" + url_parse.netloc
        links = [raw_url+i if (i[0] == '/') else i for i in deepcopy(links)]
        links_edit = [unquote(i) for i in links]
        r = re.compile(r"https:\/\/www\.goal\.com\/th\/(ข่าว|ลิสต์)\/.*")
        fil_links = list(filter(r.match, links_edit)) # Read Note
        return fil_links.copy()
    elif base_url == "https://www.siamsport.co.th/football/international":
        r = re.compile(r"https:\/\/www\.siamsport\.co\.th\/football\/.*\/view\/.*")
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    elif base_url == "https://www.soccersuck.com":
        r = re.compile(r"https:\/\/www\.soccersuck\.com\/boards\/topic\/.*")
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    elif base_url == "https://www.bbc.com/sport/football":
        r = re.compile(r"https:\/\/www\.bbc\..*\/sport\/football\/\d+")
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    elif base_url == "https://www.dailymail.co.uk/sport/football":
        r = re.compile(r'((https\:\/\/www\.dailymail\..*\/sport\/football\/article-\d+\/.*\.html)(?!#))')
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    elif base_url == "https://edition.cnn.com/sport/football":
        url_parse = urlparse(base_url)
        raw_url = url_parse.scheme + "://" + url_parse.netloc
        links = [raw_url+i if (i[0] == '/') else i for i in links]
        r = re.compile(r'https\:\/\/edition\.cnn\.com\/\d{4}\/\d{2}\/\d{2}\/football\/.*')
        fil_links = list(filter(r.match, links)) # Read Note
        return fil_links.copy()
    else:
        return links

def n_gram_count(content, word):
    return content.count(word)
    # return len(re.findall(word, content))

def get_url_links(url, content):
    if not content: return []
    url_reg2 = re.compile(r"href='(.*?)'")
    url_reg3 = re.compile(r'href="(.*?)"')
    result = re.findall(url_reg2, content)
    result += re.findall(url_reg3, content)
    result = [i.strip() for i in result.copy() if i]
    return deepcopy(result)

def write_url(l):
    with open("all_url.csv", 'r+', encoding="utf-8") as f :
        f.readlines()
        l = [i.strip()+"\n" for i in l]
        f.writelines(l)

def get_sublink(s_url):
    content = get_url_content(s_url)
    sub = get_url_links(s_url, content)
    return sub.copy()

def get_all_links(url):
    l = [url]
    sub_l = get_sublink(url)
    count = 5
    while sub_l == [] and count > 0:
        sub_l = get_sublink(url)
        count -= 1
    l += sub_l.copy()
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        results = [executor.submit(get_sublink, i) for i in sub_l]
        for result in as_completed(results):
            l += result.result()
    l = filter_links(url, l)
    write_url(l.copy())
    print(url,"success")
    return deepcopy(l)

def add_n_gram(url, word):
    con = get_url_content(url)
    if con == None:
        return (url, 0)
    n = n_gram_count(con, word)
    return (url, n)

def get_links_multithread():
    links = ["https://www.goal.com/th", "https://www.skysports.com/football", "https://www.siamsport.co.th/football/international", "https://www.soccersuck.com", 
    "https://www.bbc.com/sport/football", "https://www.dailymail.co.uk/sport/football", "https://edition.cnn.com/sport/football"]
    with open("all_url.csv", 'w', encoding="utf-8") as f :
        f.write("url\n")
    all_links = []
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        results = (executor.submit(get_all_links, link) for link in links)
        for result in as_completed(results):
            all_links += result.result()
    print("before :", len(all_links))
    fil_links = pd.Series(all_links)
    fil_links.drop_duplicates(inplace=True)
    return fil_links.values

def get_n_gram_multithread(all_links=[]):
    if len(all_links) == 0:
        all_links = get_pd('all_url2.csv')
    data = pd.DataFrame({'url':[], 'n_gram':[]})
    with concurrent.futures.ThreadPoolExecutor(2000) as executor :
        results = ( executor.submit(lambda url: add_n_gram(url, 'Ronaldo'), i) for i in all_links)
        for result in as_completed(results):
            url, n = result.result()
            data.loc[len(data.index)] = [url, n]
    data = data.sort_values(by=['n_gram'], ascending=False)
    return data


if __name__ == "__main__":
    pd.options.display.max_colwidth = 600

    start = time.time()
    all_links = get_links_multithread()
    print("links: ", len(all_links))
    print('request copleted: ', time.time()-start)
    data = get_n_gram_multithread()
    print(data[:20])
    print('total: ', time.time()-start)
