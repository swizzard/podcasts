from bs4 import BeautifulSoup as S
from dateutil import parser
import re
import requests


def get_res(url):
    return S(requests.get(url).content, 'xml')


def process_feed(res):
    chan = res.channel
    pod_info = {'link': get_link(res),
                'language': chan.language,
                'author': res.author.text or '',
                'title': res.title.text or '',
                'summary': res.summary.text or '',
                'explicit': parse_explicit(res.explicit.text),
                'categories': chan_categories(res)}
    pod_info.update(item_info(res))
    return pod_info


def parse_explicit(txt):
    if txt is None:
        return False
    elif re.match(r'(1|[Tt]rue|[Yy]es)', txt):
        return True
    else:
        return False


def parse_duration(dur_str):
    grps = re.findall(r'(\d+):?', dur_str)
    dur = 0
    for idx, grp in enumerate(reversed(grps)):
        dur += int(grp) * (60 ** idx)
    return dur


def get_durs(items):
    durs = []
    for item in items:
        if ite.duration is not None:
            durs.append(parse_duration(item.duration.text))
        elif item.content is not None:
            dur = item.content.get('duration')
            if dur is not None:
                dur = int(dur)
            durs.append(dur)
    return durs


def item_info(res):
    items = res.find_all('item')
    item_info = {}
    try:
        item_info['pubs'] = [parser.parse(item.pubDate.text) for item in items]
    except (AttributeError, ValueError):
        pass
    try:
        item_info['durs'] = get_durs(items)
    except (AttributeError, TypeError, ValueError):
        pass
    try:
        item_info['descs'] = [S(item.description.text, 'lxml').text
                              for item in items]
    except (AttributeError, TypeError, ValueError):
        pass
    return item_info


def chan_categories(res):
    def itcat(tag):
        return tag.name == 'category' and \
               tag.namespace == 'http://www.itunes.com/dtds/podcast-1.0.dtd'
    return {cat['text'] for cat in res.find_all(itcat)}


def get_link(res):
    funcs = [lambda tag: tag.type == 'application/rss+xml',
             lambda tag: tag.namespace == 'http://www.w3.org/2005/Atom',
             lambda tag: '.rss' in tag.get('href', '')]
    links = [res.find(func) for func in funcs]
    return links[0] if links else None


def main(url):
    return process_feed(get_res(url))

