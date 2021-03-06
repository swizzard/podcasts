import logging

from bs4 import BeautifulSoup as S
from dateutil import parser
import re
from requests import RequestException


class Parser():
    def __init__(self, session):
        self.session = session

    def parse_feed(self, url):
        if url:
            logging.info('{}'.format(url))
            res, url = self.get_res(url)
            return self.process_feed(res, url)

    def process_feed(self, res, url):
        if res:
            pod_info = {'link': url}
            try:
                chan = res.channel
                if chan is None:
                    return
                else:
                    pod_info['language'] = self.get_text(chan, 'language')
                    pod_info['author'] = self.get_text(chan, 'author')
                    pod_info['title'] = self.get_text(chan, 'title')
                    pod_info['summary'] = self.get_text(chan, 'summary')
                    pod_info['homepage'] = self.get_text(chan, 'link')
                    explicit = self.get_text(chan, 'explicit')
                    pod_info['explicit'] = self.parse_explicit(explicit)
                    pod_info['categories'] = self.chan_categories(chan)
                    pod_info['episodes'] = self.get_episodes(chan)
            except (AttributeError, TypeError):
                logging.exception('url: {}'.format(url))
            else:
                return pod_info

    def get_episodes(self, res):
        items = res.find_all('item')
        out = []
        for item in items:
            try:
                pub = parser.parse(item.pubDate.text)
            except (TypeError, ValueError):
                pub = None
            try:
                desc = self.fmt_text(S(item.description.text, 'lxml').text)
            except (TypeError, AttributeError):
                desc = ''
            dur = self.get_dur(item)
            out.append({'title': self.fmt_text(item.title.text)[:191],
                        'week_day': pub.weekday() if pub else None,
                        'day_of_month': pub.day if pub else None,
                        'date': pub,
                        'duration': dur,
                        'description': desc[:49087]})
        return out

    def get_res(self, url):
        body = None
        link = None
        try:
            req = self.session.get(url, timeout=120.0)
        except RequestException:
            logging.exception('url: {}'.format(url))
        else:
            if req.ok:
                body = S(req.content, 'xml')
                link = req.url
            else:
                logging.error('got {} retrieving {}'.format(req.status_code,
                                                            req.url))
        return body, link

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

    def get_dur(self, item):
        dur = 0
        if item.duration is not None:
            dur = self.parse_duration(item.duration.text)
        elif item.content is not None:
            dur = item.content.get('duration', 0)
        return dur

    def chan_categories(self, res):
        def itcat(tag):
            return tag.name == 'category' and \
                tag.namespace == 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return {self.fmt_text(cat.get('text', '')) for cat in
                res.find_all(itcat)}

    def get_text(self, res, attr):
        a = getattr(res, attr)
        if hasattr(a, 'text'):
            return self.fmt_text(a.text) or ''
        else:
            return ''

    @staticmethod
    def fmt_text(txt):
        return txt.strip()

