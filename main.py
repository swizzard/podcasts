import logging
import sys

import requests

from parse import Parser
from post_process import expected_dur, pub_schedule
from scrape import Scraper
from store import DummyStorage, Storage


class Pipeline():
    def __init__(self, dry=False):
        self.session = requests.Session()
        self.session.headers = {'user-agent': 'shr-podcasts-bot'}
        self.scraper = Scraper(self.session)
        self.parser = Parser(self.session)
        self.storage = DummyStorage() if dry else Storage()

    def run(self, root, start_page):
        feeds = self.scraper.scrape(root, start_page) or []
        for feed in feeds:
            pod_info = self.parser.parse_feed(feed)
            if pod_info is not None:
                pod_info['expected_dur'] = expected_dur(pod_info)
                schedule_info = pub_schedule(pod_info)
                pod_info.update(schedule_info)
                self.storage.store_podcast(pod_info)
                logging.info('stored %s', pod_info)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    pipeline = Pipeline()
    pipeline.run("https://www.blubrry.com", "/programs")

