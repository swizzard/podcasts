from bs4 import BeautifulSoup as S
import requests


class Scraper():
    def __init__(self):
        self.root = "https://www.blubrry.com"

    def scrape_cats(self):
        for tag in self.get_soup('/programs').find_all(
                self.class_fil('category-box')):
            link = self.get_link(tag.a)
            if link:
                yield link

    def scrape_cat_page(self, cat_link, page=0):
        tags = self.get_soup(cat_link, {'pi': page}).find_all(
            self.class_fil('item-box'))
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
        res = requests.get(self.root + url, params=params)
        return S(res.content, 'lxml')

    @staticmethod
    def class_fil(class_name):
        return lambda tag: class_name in tag.attrs.get('class', [])

    @staticmethod
    def get_link(tag):
        return tag.attrs.get('href')


def main():
    scraper = Scraper()
    links = []
    for cat in scraper.scrape_cats():
        for podcast in scraper.scrape_cat_page(cat):
            yield scraper.scrape_feed_url(podcast)

