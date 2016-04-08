import logging 

from bs4 import BeautifulSoup as S
from requests.exceptions import RequestException


class Scraper():
    def __init__(self, session):
        self.session = session
        self.root = None

    def scrape(self, root, start_page):
        self.root = root
        for cat in self.scrape_cats(start_page):
            for podcast in self.scrape_cat_page(cat):
                yield self.scrape_feed_url(podcast)

    def scrape_cats(self, start_page):
        for tag in self.get_soup(start_page).find_all(
                self.class_fil('category-box')):
            link = self.get_link(tag.a)
            if link:
                yield link

    def scrape_cat_page(self, cat_link, page=0):
        try:
            tags = self.get_soup(cat_link, {'pi': page}).find_all(
                self.class_fil('item-box'))
        except AttributeError:
            logging.exception('%s (page %s)', cat_link, page)
            tags = []
        if tags:
            for tag in tags:
                link = self.get_link(tag.a)
                if link:
                    yield link
            else:
                page += 1
                for link in self.scrape_cat_page(cat_link, page=page):
                    yield link

    def scrape_feed_url(self, link):
        links = self.get_soup(link + 'more-info').find_all('a')
        for link in links:
            if link.text == 'RSS Podcast Feed':
                return self.get_link(link)

    def get_soup(self, url, params=None):
        params = params or {}
        full_url = self.root + url
        try:
            res = self.session.get(full_url, params=params)
            res.raise_for_status()
        except RequestException:
            logging.exception('url: %s\nparams: %s', full_url, params)
        else:
            return S(res.content, 'lxml')

    @staticmethod
    def class_fil(class_name):
        return lambda tag: class_name in tag.attrs.get('class', [])

    @staticmethod
    def get_link(tag):
        return tag.attrs.get('href')


