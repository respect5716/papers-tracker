import os
import re
import requests
from bs4 import BeautifulSoup

import arxiv
import pandas as pd

import smtplib
from email.mime.text import MIMEText


def read_seeds(fpath):
    id_list = open(fpath, 'r').read().split('\n')
    id_list = [i for i in id_list if i]
    res = arxiv.Search(id_list=id_list).results()
    title_list = [r.title for r in res]
    seeds = pd.DataFrame({'title': title_list, 'arxiv_id': id_list})
    return seeds

def url_to_soup(url):
    res = requests.get(url)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_cites_url(arxiv_id, start=0):
    soup = url_to_soup(f'https://scholar.google.com/scholar_lookup?arxiv_id={arxiv_id}')
    hrefs = [a.get('href') for a in soup.select('a')]
    hrefs = [h for h in hrefs if 'scholar?cites' in h]
    if hrefs:
        cites = 'https://scholar.google.com' + hrefs[0] + f'&start={start}&scisbd=1'
    else:
        cites = None
    return cites


def get_citing_papers(arxiv_id, age=3):
    res = pd.DataFrame(columns=['title', 'url', 'age'])

    start = 0
    while True:
        cites_url = get_cites_url(arxiv_id, start=start)
        if not cites_url: break
            
        soup = url_to_soup(cites_url)
        papers = soup.select('h3.gs_rt')

        ages = [i.text for i in soup.select('span.gs_age')]
        ages = [''.join(filter(str.isdigit, a)) for a in ages]
        titles = [i.a.text for i in papers]
        urls = [i.a.get('href') for i in papers]

        _res = pd.DataFrame({'title': titles, 'url': urls, 'age': ages})
        _res = _res.loc[_res['age'] == str(age)]

        res = pd.concat([res, _res], ignore_index=True)
        start += 10
        
        if len(_res) == 0:
            break

    return res


def write_doc(seeds, citations):
    text = "오늘의 논문\n\n"
    text += '=' * 50 + '\n'

    for idx, row in seeds.iterrows():
        text += row['title'] + '\n\n\n'
        cites = citations[row['arxiv_id']]
        for _idx, _row in cites.iterrows():
            text += _row['title'] + '\n'
            text += _row['url'] + '\n\n'

        text += '=' * 50 + '\n'
    
    return text


def main():
    seeds = read_seeds('papers.txt')

    citations = {}
    for idx, row in seeds.iterrows():
        arxiv_id = row['arxiv_id']
        citations[arxiv_id] = get_citing_papers(arxiv_id)
    
    doc = write_doc(seeds, citations)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()  # TLS 사용시 필요
    smtp.login(os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_PASSWORD'])

    msg = MIMEText(doc)
    msg['Subject'] = '오늘의 논문'
    msg['To'] = os.environ['EMAIL_ADDRESS']
    smtp.sendmail(os.environ['EMAIL_ADDRESS'], os.environ['EMAIL_ADDRESS'], msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    main()