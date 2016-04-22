from copy import copy
from datetime import datetime
from functools import partial
import hashlib
import json
import logging
from os import path, urandom, walk
import re

import falcon
import redis

import models


class DBEncoder(json.JSONEncoder):
    def default(self, obj):
        podcast = partial(self.to_dict, ['id', 'episode_count', 'explicit',
                                         'feed_url', 'homepage', 'language',
                                         'summary', 'title'])
        episode = partial(self.to_dict, ['id', 'date', 'description', 'duration',
                                         'podcast_id', 'title', 'week_day',
                                         'day_of_month'])
        category = partial(self.to_dict, ['id', 'name'])
        user = partial(self.to_dict, ['id', 'name', 'email', 'public'])
        mapping = {models.Podcast: podcast,
                   models.Episode: episode,
                   models.Category: category,
                   models.User: user,
                   datetime: lambda d: d.isoformat()}
        default = partial(json.JSONEncoder.default, self)
        return mapping.get(type(obj), default)(obj)

    def to_dict(self, attrs, obj):
        out = {name: getattr(obj, name, None) for name in attrs}
        return out


class Noncer():
    conn = None

    def __init__(self):
        if Noncer.conn is None:
            cfg_path = self.find_config()
            with open(cfg_path) as cfg_fil:
                cfg = json.load(cfg_fil)
            Noncer.conn = redis.Redis(host=cfg['redis_host'])
        self.timeout = 86400
        self._nonce = None
        self._expiration = None

    @property
    def nonce(self):
        if self._nonce is None:
            nonce = self.conn.get('nonce')
            if nonce is None:
                nonce = urandom(16)
                self.conn.set('nonce', nonce)
                self.conn.expire('nonce', self.timeout)
            self._nonce = nonce
        return self._nonce

    @property
    def expiration(self):
        if self._expiration is None:
            self._expiration = self.conn.ttl('nonce')
        return self._expiration

    def get_token(self, username):
        return hashlib.md5(self.nonce + username.encode()).hexdigest()

    def validate_token(self, username, token):
        expected_token = self.get_token(username)
        return expected_token == token

    @staticmethod
    def find_config():
        def get_config(dirname, subdirs, fils):
            if 'config.json' in fils:
                return path.abspath(path.join(dirname, 'config.json'))
            else:
                while subdirs[0][0] in {'.', '_'}:
                    del subdirs[0]
        walker = walk('.')
        cfg_pth = get_config(*next(walker))
        while cfg_pth is None:
            try:
                cfg_pth = get_config(*next(walker))
            except StopIteration:
                break
        return cfg_pth


class Validator():
    def __init__(self):
        self.noncer = Noncer()
        self.username_header = 'X-AUTH-USER'
        self.token_header = 'X-AUTH-TOKEN'

    def validate(self, user_name, user_id, req):
        try:
            header_name = req.headers[self.username_header]
            token = req.headers[self.token_header]
        except KeyError as err:
            logging.exception(req.headers)
            raise falcon.HTTPMissingHeader(err.args[0])
        else:
            if user_name == header_name:
                return self.noncer.validate_token(user_name, token)
            return False

    def can_view(self, user_public, user_name, user_id, req):
        if user_public:
            return True
        else:
            return self.validate(user_name, user_id, req)


class Paginator():
    limit = 25

    def __init__(self):
        self.page = 1

    @property
    def start(self):
        return (self.page - 1) * self.limit

    @property
    def next_page(self):
        return self.page + 1

    @property
    def prev_page(self):
        if self.page > 1:
            return self.page - 1

    def paginate_query(self, query):
        query = query.offset(self.start).limit(self.limit)
        res = query.all()
        if res:
            self.page += 1
        return res

    def paginate_qs(self, req):
        page = req.get_param_as_int('page')
        if page is None:
            prev = None
            pth = req.uri
            if '?' in pth:
                nxt = pth + '&page=2'
            else:
                nxt = pth + '?page=2'
        else:
            self.page = page
            prev = None
            page_pat = re.compile(r'(page=){}'.format(page))
            pagination = {'prev': None, 'next': None}
            if self.prev_page:
                prev = re.sub(page_pat, r'\g<1>{}'.format(self.prev_page), req.uri)
            nxt = re.sub(page_pat, r'\g<1>{}'.format(self.next_page), req.uri)
        return {'prev': prev, 'next': nxt}

    def paginate(self, req, query):
        pagination = self.paginate_qs(req)
        res = self.paginate_query(query)
        return pagination, res

    @staticmethod
    def reconstruct_qs(**kwargs):
        return '?{}'.format('&'.join('{}={}'.format(k,v) for k,v in
                                     kwargs.items()))

    @staticmethod
    def _cupdate(d, **kwargs):
        cpy = copy(d)
        cpy.update(kwargs)
        return cpy


def validate_rel_type(rel_type):
    if rel_type not in {'likes', 'likers', 'dislikes', 'dislikers'}:
        raise falcon.HTTPNotFound


