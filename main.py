import os
import re
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

import arxiv
import pandas as pd

import smtplib
from email.mime.text import MIMEText


def get_target_date(delta=-3):
    now = datetime.utcnow()
    date = now + timedelta(days=delta)
    date = date.strftime('%Y%m%d')
    return date


def read_seeds(fpath):
    id_list = open(fpath, 'r').read().split('\n')
    id_list = [i for i in id_list if i]
    res = arxiv.Search(id_list=id_list).results()
    title_list = [r.title for r in res]
    seeds = pd.DataFrame({'title': title_list, 'arxiv_id': id_list})
    return seeds


def find_followers_id_list(arxiv_id, yymm, limit=100):
    url = f'https://api.semanticscholar.org/v1/paper/arXiv:{arxiv_id}'
    res = requests.get(url).json()
    if res.get('error'):
        return []
    followers = pd.DataFrame(res['citations'])
    if len(followers) == 0:
        return []
        
    followers = followers.dropna(subset=['arxivId'])
    followers = followers.loc[followers['arxivId'].apply(lambda x: x.split('.')[0] == yymm)]
    followers = followers.sort_values('arxivId', ascending=False)
    id_list = followers['arxivId'].iloc[:limit].tolist()
    return id_list


def search_followers(fid_list):
    if not fid_list:
        return pd.DataFrame(columns=['title', 'url', 'date'])
    
    res = arxiv.Search(id_list=fid_list).results()
    followers = []
    for r in res:
        followers.append({'title': r.title, 'url': r.entry_id, 'date': r.published.strftime('%Y%m%d')})
    followers = pd.DataFrame(followers)
    return followers




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
    date = get_target_date()
    seeds = read_seeds('papers.txt')

    citations = {}
    for idx, row in seeds.iterrows():
        arxiv_id = row['arxiv_id']
        fid_list = find_followers_id_list(arxiv_id, date[2:-2])
        followers = search_followers(fid_list)
        followers = followers.loc[followers['date'] == date]
        citations[arxiv_id] = followers
        print(f'{arxiv_id} finished')
        time.sleep(10)


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