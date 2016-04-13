from functools import partial
import json
import logging

import falcon
from sqlalchemy.exc import SQLAlchemyError

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
        user = partial(self.to_dict, 
        mapping = {models.Podcast: self.podcast,
                   models.Episode: self.episode,
                   models.Category: self.category,
                   models.User: self.user}
        return mapping.get(type(obj), super().default)(obj)

    @staticmethod
    def to_dict(attrs, obj):
        return super().default({name: getattr(obj, name, None) for name in attrs})


class DBResource():
    session = None

    def __init__(self):
        if DBResource.session is None:
            DBResource.session = models.Session()

    def handle_db_err(self, err, resp):
        resp.status = falcon.HTTP_500
        resp.body = json.dumps({'type': err.__class__.__name__,
                                'args': err.args})
        self.session.rollback()


class PodcastResource(DBResource):
    def handle_res(self, ress, resp):

    def on_get(self, req, resp, podcast_id=None):
        if podcast_id is not None:

