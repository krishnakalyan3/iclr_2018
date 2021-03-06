#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import pandas as pd
from random import randint
from time import sleep

# TODO
# Total Revisions
# Total Comments
# Average Rating
# Average Confidence

class Scraper(object):

    def __init__(self):
        self.url = 'https://iclr.cc/Conferences/2018/Schedule'
        self.sleep_min = 0
        self.sleep_max = 3
        self.count = 0

    def scrape_open_review(self, open_review_url):
        sleep_interval = randint(self.sleep_min, self.sleep_max)
        sleep(sleep_interval)
        print('url: {} count: {} sleep: {}'.format(open_review_url, self.count, sleep_interval))
        open_res = requests.get(open_review_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = BeautifulSoup(open_res.content, 'html.parser')
        data = self.get_data(html)

        return data

    def get_data(self, data):
        date = data.find("span", class_="date item")
        abstracts = data.find_all("span", class_="note-content-value")

        if len(abstracts) == 1:
            abstract = abstracts
            return date.text, abstract[0].text, '', ''
        elif len(abstracts) == 2:
            abstract, keywords = abstracts
            return date.text, abstract.text, '', keywords.text
        else:
            abstract, tldr, keywords = abstracts
            return date.text, abstract.text, tldr.text, keywords.text

    def get_type_data(self, html, type='Oral'):
        data = {'type': [],
                'title': [],
                'authors': [],
                'url': [],
                'submission_date': [],
                'abstract': [],
                'tldr': [],
                'keywords': []}

        title = html.find_all("div", class_="maincard narrower {}".format(type))
        for item in title:
            self.count += 1
            title = item.find("div", class_="maincardBody")
            authors = item.find("div", class_="maincardFooter")

            if not type == 'InvitedTalk':
                url = item.find("a", class_="btn btn-default btn-xs href_PDF").get('href')
                date, abstract, tldr, keywords = self.scrape_open_review(url)

                data['type'].append(type)
                data['title'].append(' '.join(title.contents))
                data['authors'].append(' '.join(authors.contents))
                data['url'].append(url)
                data['submission_date'].append(date)
                data['abstract'].append(abstract)
                data['tldr'].append(tldr)
                data['keywords'].append(keywords)

        return pd.DataFrame(data)

    def scrape_site(self):
        res = requests.get(self.url)
        html = BeautifulSoup(res.content, 'html.parser')

        if html:
            data_oral = self.get_type_data(html, 'Oral')
            data_invited_talk = self.get_type_data(html, 'InvitedTalk')
            data_poster = self.get_type_data(html, 'Poster')
            data_workshop = self.get_type_data(html, 'Workshop')

        data = pd.concat([data_oral, data_invited_talk, data_poster, data_workshop], axis=0)
        data['index'] = data.index

        return pd.DataFrame(data)


if __name__ == '__main__':
    scrape = Scraper()
    data = scrape.scrape_site()
    data.to_csv('../data/iclr.csv', index=False)
