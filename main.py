import logging
import os
import sys

import requests

from parse import Parser
from post_process import expected_dur, pub_schedule
from scrape import Scraper
from store import DummyStorage, Storage


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
    log_fmt = '%(asctime)s %(levelname)s %(funcName)s| %(message)s'
    logging.basicConfig(filename=os.path.join(os.getcwd(), 'podcasts.log'),
                        format=log_fmt)
    pipeline = Pipeline()
    pipeline.run("https://www.blubrry.com", "/programs")

