from asyncio import as_completed
import re
import requests
import threading
import pandas as pd
import concurrent.futures
from concurrent.futures import as_completed
import numpy as np

def get_pd(filename):
    d = pd.read_csv(filename, index_col=False, on_bad_lines='skip')
    d = d.drop_duplicates(subset=['url'])
    return d

def get_url_content(link):
    try:
        r = requests.get(link, timeout=5)
        html_text = r.text
        return html_text
    except requests.exceptions.Timeout:
      print( "Timeout occurred")

def n_gram_count(content, word):
    return len(re.findall(word, content))

def get_url_links(url, content):
    url = url.split('.com')[0]+'.com'
    url_reg2 = re.compile(r"href='(.*?)'")
    url_reg3 = re.compile(r'href="(.*?)"')
    result = re.findall(url_reg2, content)
    result += re.findall(url_reg3, content)
    result = [i.strip() for i in result if i]
    result = [url+i for i in result if (i[0] == '/' and len(i)>1)]
    return result

def write_url(l):
    with open("all_url.csv", 'r+') as f :
        f.readlines()
        l = [i.strip()+"\n" for i in l]
        f.writelines(l)

def get_all_links(url):
    def get_sublink(url):
        content = get_url_content(url)
        sub = get_url_links(url, content)
        return sub.copy()
    l = [url]
    sub_l = get_sublink(url)
    l += sub_l.copy()
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        results = [executor.submit(get_sublink, i) for i in sub_l]
        for result in as_completed(results):
            l += result.result()
    write_url(l.copy())
    print(url,"success")

def clear_file():
    with open("all_url.csv", 'w') as f :
        f.write('url\n')
    with open("all_url2.csv", 'w') as f :
        f.write('url,n_gram\n')

def add_n_gram(url):
    con = get_url_content(url)
    if con == None:
        return (url, 0)
    n = n_gram_count(con, 'Barca')
    # with open("all_url2.csv", 'r+') as f :
    #     f.readlines()
    #     f.write(url+','+str(n)+"\n")
    return (url, n)

if __name__ == "__main__":
    pd.options.display.max_colwidth = 600
    link = ["https://www.goal.com/th", "https://www.skysports.com/football/news"]
    # print(get_url_content(link[0]))
    # treads = []
    # word = 'Arsenal'
    # clear_file()
    # with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        # executor.map(get_all_links, link)

    d = get_pd("all_url.csv")
    print(len(d))
    with open("all_url2.csv", 'w') as f :
        f.write('url,n_gram\n')
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        # results = executor.map(add_n_gram, d['url'].values.tolist())
        results = ( executor.submit(add_n_gram, i) for i in d['url'].values.tolist() )
        for result in as_completed(results):
            url, n = result.result()
            with open("all_url2.csv", 'r+') as f :
                f.readlines()
                f.write(url+','+str(n)+"\n")


    d = get_pd("all_url2.csv")
    a = d.sort_values(by=['n_gram'], ascending=False)
    print(a[:20])
