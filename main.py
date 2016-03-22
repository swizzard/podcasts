from parse import Parser
from post_process import expected_dur, pub_schedule
from scrape import Scraper
from store import Storage


class Pipeline():
    def __init__(self):
        self.parser = Parser()
        self.storage = Storage()

    def run(self, root, start_page):
        scraper = Scraper(root, start_page)
        feeds = scraper.scrape()
        for feed in feeds:
            pod_info = self.parser.parse(feed)
            pod_info['expected_dur'] = expected_dur(pod_info)
            schedule_info = pub_schedule(pod_info)
            pod_info.update(schedule_info)
            self.storage.store_podcast(pod_info)


if __name__ == '__main__':
    pipeline = Pipeline()
    pipeline.run("https://www.blubrry.com", "/programs")

