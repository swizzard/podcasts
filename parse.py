from bs4 import BeautifulSoup as S
from dateutil import parser
import re
import requests


class Parser():
    def __init__(self):
        pass

    def parse_feed(self, url):
        res = self.get_res(url)
        return self.process_feed(res)        

    def process_feed(self, res):
        chan = res.channel
        pod_info = {'link': self.get_link(res),
                    'language': chan.language,
                    'author': res.author.text or '',
                    'title': res.title.text or '',
                    'summary': res.summary.text or '',
                    'explicit': self.parse_explicit(res.explicit.text),
                    'categories': self.chan_categories(res)}
        pod_info.update(self.item_info(res))
        return pod_info

    def item_info(self, res):
        items = res.find_all('item')
        item_info = {}
        try:
            item_info['pubs'] = [parser.parse(item.pubDate.text) for item in
                                 items]
        except (AttributeError, ValueError):
            pass
        try:
            item_info['durs'] = self.get_durs(items)
        except (AttributeError, TypeError, ValueError):
            pass
        try:
            item_info['descs'] = [S(item.description.text, 'lxml').text for
                                  item in items]
        except (AttributeError, TypeError, ValueError):
            pass
        return item_info

    @staticmethod
    def get_res(url):
        return S(requests.get(url).content, 'xml')

    @staticmethod
    def parse_explicit(txt):
        if txt is None:
            return False
        elif re.match(r'(1|[Tt]rue|[Yy]es)', txt):
            return True
        else:
            return False

    @staticmethod
    def parse_duration(dur_str):
        grps = re.findall(r'(\d+):?', dur_str)
        dur = 0
        for idx, grp in enumerate(reversed(grps)):
            dur += int(grp) * (60 ** idx)
        return dur

    def get_durs(self, items):
        durs = []
        for item in items:
            if ite.duration is not None:
                durs.append(self.parse_duration(item.duration.text))
            elif item.content is not None:
                dur = item.content.get('duration')
                if dur is not None:
                    dur = int(dur)
                durs.append(dur)
        return durs

    @staticmethod
    def chan_categories(res):
        def itcat(tag):
            return tag.name == 'category' and \
                tag.namespace == 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return {cat['text'] for cat in res.find_all(itcat)}

    @staticmethod
    def get_link(res):
        funcs = [lambda tag: tag.type == 'application/rss+xml',
                lambda tag: tag.namespace == 'http://www.w3.org/2005/Atom',
                lambda tag: '.rss' in tag.get('href', '')]
        links = [res.find(func) for func in funcs]
        return links[0] if links else None

