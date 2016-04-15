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
        user = partial(self.to_dict, ['name', 'email', 'public'])
        mapping = {models.Podcast: podcast,
                   models.Episode: episode,
                   models.Category: category,
                   models.User: user}
        return mapping.get(type(obj), super().default)(obj)

    @staticmethod
    def to_dict(attrs, obj):
        return super().default({name: getattr(obj, name, None) for name in attrs})


class InvalidSubcoll(falcon.HTTPNotFound):
    def __init__(self, model, invalid, valid, path):
        super().__init__(self)
        self.model_name = model.__name__
        self.path = path
        self.invalid = invalid
        self.valid = valid

    def to_dict(self, obj_type=dict):
        out = obj_type()
        out['path'] = self.path
        msg = '{} is not a valid subcollection of {}. Please choose from\n'
        msg = msg.format(invalid, self.model_name) + '\n'.join(self.valid)
        out['message'] = msg
        return out


class MissingSubcollParent(falcon.HTTPNotFound):
    def __init__(self, model, obj_id, path):
        super().__init__(self)
        self.model_name = model.__name__
        self.path = path
        self.obj_id = obj_id

    def to_dict(self, obj_type=dict):
        out = obj_type()
        out['path'] = self.path
        msg = 'No {} with id {}'.format(self.model_name, self.obj_id)
        out['message'] = msg
        return out


class DBResource():
    session = None

    def __init__(self):
        if DBResource.session is None:
            DBResource.session = models.Session()
        self.dumps = partial(json.dumps, cls=DBEncoder)

    def handle_db_err(self, err, req, resp):
        resp.status = falcon.HTTP_500
        resp.body = self.dumps({'path': req.path,
                                'type': err.__class__.__name__,
                                'args': err.args})
        self.session.rollback()

    def handle_res(self, objs, req, resp, model=self.model):
        out = {'path': req.path,
               'type': self.model.__name__,
               'result': objs}
        resp.body = self.dumps(out)

    def handle_one(self, obj, req, resp):
        if obj is None:
            obj = []
        else:
            obj = [obj]
        self.handle_res(obj, req, resp)

    def get_by_id(self, req, resp, obj_id):
        obj = self.session.query(self.model).get(obj_id)
        self.handle_one(obj, req, resp)


class PodcastResource(DBResource):
    model = models.Podcast

    def on_get(self, req, resp, podcast_id, subres=None):
        if podcast_id is not None:
            self.get_by_id(int(podcast_id))


class SubcollMixin(DBResource):
    subcolls = {'categories': models.Category,
                'episodes': models.Episode,
                'likers': models.User,
                'dislikers': models.User}

    def on_get(self, req, resp, obj_id, subcoll_name):
        try:
            subcoll_model = self.subcolls[subcoll_name]
        except KeyError:
            raise InvalidSubcoll(self.model, subcoll_name, self.subcolls.keys(),
                                 req.path)
        else:
            podcast = self.session.query(models.Podcast).get(podcast_id)
            if res is None:
                raise MissingSubcollParent(self.model, podcast_id, req.path)
            else:
                objs = getattr(podcast, subcoll_name)
                self.handle_res(objs, req, resp, model=subcoll_model)


class PodcastsResource(DBResource):
    model = models.Podcast

    def on_get(self, req, resp):
            filts = []
            queries = [(req.get_param('title'),
                        lambda t: models.Podcast.title.like('{}%'.format(t))),
                       (req.get_param('author'),
                        lambda a: models.Podcast.author.like('{}%'.format(a))),
                       (req.get_param('homepage'),
                        lambda p: models.Podcast.homepage == p)]
            for param, f in queries:
                if param:
                    filts.append(f(param))
            try:
                podcasts = self.session(Podcast).query(*filts).all()
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, resp)
            else:
                self.handle_res(podcasts, req, resp) 
