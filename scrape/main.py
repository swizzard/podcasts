import logging
import os
import sys

log_fmt = '%(asctime)s %(levelname)s %(funcName)s| %(message)s'
handler = logging.FileHandler(os.path.join(os.getcwd(), 'podcasts.log'),
                              mode='w', encoding='utf-8')
logging.basicConfig(format=log_fmt, handlers=[handler], level=logging.INFO)

import requests

from parse import Parser
from post_process import expected_dur, pub_schedule
from scrape import Scraper
from store import Storage


class Pipeline():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'shr-podcasts-bot'}
        self.scraper = Scraper(self.session)
        self.parser = Parser(self.session)
        self.storage = Storage()

    def run(self, root, start_page):
        podcasts = (self.parser.parse_feed(feed) for feed in
                    self.scraper.scrape(root, start_page))
        for podcast in filter(None, podcasts):
            self.storage.store_podcast(podcast)


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.run("https://www.blubrry.com", "/programs")

