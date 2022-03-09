import requests
import urllib3
from urllib.request import urlopen
from bs4 import BeautifulSoup
import certifi
import pandas as pd
import io
import concurrent.futures
from concurrent.futures import as_completed
import time
import http.client

def read_content_request(url):
    try:
        raw = requests.get(url, timeout=3)
        content = raw.text
        return 0
    except:
        print(f'err: {url}')
        return 1

def read_content_urlopen(url):
    try:
        html = urlopen(url)
        content = html.read().decode('utf-8')
        return 0
    except:
        print(f'err: {url}')
        return 1

def read_content_urllib3(url):
    try:
        http = urllib3.PoolManager(
                cert_reqs='CERT_REQUIRED', 
                ca_certs=certifi.where()
                )
        resp = http.request("GET", links['url'][0], preload_content=False, timeout=3)
        resp.auto_close = False
        text = io.TextIOWrapper(resp)
        content = (i for i in text)
        content = "".join(content)
        return 0
    except:
        print(f'err: {url}')
        return 1

data = pd.DataFrame({'Amount of link':[100, 500, 1000, 1500]})

links = pd.read_csv('all_url.csv', on_bad_lines='skip')
links = links.drop_duplicates(subset=['url'])
print(len(links))

print('request')
for i in [100, 500, 1000, 1500]:
    start = time.time()
    err = 0
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        out = ( executor.submit(read_content_request, k) for k in links['url'][:i])
        for re in concurrent.futures.as_completed(out):
            err += re.result()
    result = time.time() - start
    data.loc[data['Amount of link'] == i, 'requests'] = result
    data.loc[data['Amount of link'] == i, 'Amount of request error'] = err
print('request')
    
print('\nurllib3')
for i in [100, 500, 1000, 1500]:
    start = time.time()
    err = 0
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        out = ( executor.submit(read_content_urllib3, k) for k in links['url'][:i])
        for re in concurrent.futures.as_completed(out):
            err += re.result()
    result = time.time() - start
    data.loc[data['Amount of link'] == i, 'urllib3'] = result
    data.loc[data['Amount of link'] == i, 'Amout of urllib3 error'] = err
print('urllib3')

print('\nurlopen')
for i in [100, 500, 1000, 1500]:
    start = time.time()
    err = 0
    with concurrent.futures.ThreadPoolExecutor(1000) as executor :
        out = (executor.submit(read_content_urlopen, k) for k in links['url'][:i])
        for re in concurrent.futures.as_completed(out):
            err += re.result()
    result = time.time() - start
    data.loc[data['Amount of link'] == i, 'urlopen'] = result
    data.loc[data['Amount of link'] == i, 'Amout of urlopen error'] = err
print('urlopen')

print(data)
