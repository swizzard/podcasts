from parse import Parser
from post_process import expected_dur, pub_schedule
from scrape import Scraper
from store import DummyStorage, Storage


class Pipeline():
    def __init__(self, dry=False):
        self.parser = Parser()
        self.storage = DummyStorage() if dry else Storage()

    def run(self, root, start_page, max_=None):
        scraper = Scraper(root, start_page)
        feeds = scraper.scrape()
        count = 0
        for feed in feeds:
            if not max_ or count < max_:
                pod_info = self.parser.parse_feed(feed)
                if pod_info is not None:
                    pod_info['expected_dur'] = expected_dur(pod_info)
                    schedule_info = pub_schedule(pod_info)
                    pod_info.update(schedule_info)
                    self.storage.store_podcast(pod_info)
                    count += 1
            else:
                break


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.run("https://www.blubrry.com", "/programs")
