from datetime import datetime
import json

from sqlalchemy.exc import SQLAlchemyError

import models
from api.resources.base import DBResource
from api.resources.helpers import Paginator, validate_rel_type


class PodcastResource(DBResource):
    def __init__(self):
        super().__init__(models.Podcast)

    def on_get(self, req, resp, podcast_id):
        podcast = self.session.query(models.Podcast).get(podcast_id)
        self.handle_one(podcast, req, resp)


class PodcastCategoriesResource(DBResource):
    def __init__(self):
        super().__init__(models.Podcast)
        self.paginator = Paginator()

    def on_get(self, req, resp, podcast_id):
        if not self.session.query(models.Podcast).filter_by(
            id=podcast_id).count():
            self.handle_one(None, req, resp)
        else:
            query = self.session.query(models.Category).filter(
                models.Category.podcasts.any(models.Podcast.id == podcast_id))
            try:
                pagination, res = self.paginator.paginate(req, query)
                self.handle_res(res, req, resp, models.Category,
                                 pagination=pagination)
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, resp)



class PodcastUsersResource(DBResource):
    def __init__(self):
        super().__init__(models.Podcast)
        self.paginator = Paginator()

    def on_get(self, req, resp, podcast_id, rel_type):
        validate_rel_type(rel_type)
        try:
            if not self.session.query(models.Podcast).filter_by(
                id=podcast_id).count():
                self.handle_one(None, req, resp)
            else:
                query = self.session.query(models.User).filter(
                    User.public == True,
                    User.likes.any(models.Podcast.id == podcast_id))
                try:
                    pagination, res = self.paginator.paginate(req, query)
                except SQLAlchemyError as err:
                    self.handle_db_err(err, req, resp)
                else:
                    self.handle_res(res, req, resp, models.User,
                                    pagination=pagination)
        except SQLAlchemyError as err:
            self.handle_db_err(err, res, req)
        

class SearchResource(DBResource):
    model = models.Podcast
    limit = 25

    def __init__(self):
        super().__init__(models.Podcast)
        self.queries = [('title', self.title_filter),
                        ('author', self.author_filter),
                        ('homepage', lambda p: models.Podcast.homepage == p),
                        ('day_of_week', self.dow_filter),
                        ('day_of_month', self.dom_filter),
                        ('length', lambda d: models.Podcast.longer_than(d)),
                        ('category', self.category_filter),
                        ('published_since', self.published_since_filter),
                        ('language', lambda l: models.Podcast.language == l)]

    def on_post(self, req, resp):
        js_query = json.loads(req.stream.read().decode())
        filts = []
        for param, f in self.queries:
            value = js_query.get(param)
            if value:
                filts.append(f(value))
        db_query = self.session.query(self.model).filter(*filts)
        page = js_query.get('page', 1)
        if page > 1:
            db_query = db_query.offset(self.limit * page)
        db_query = db_query.limit(self.limit)
        try:
            res = db_query.all()
        except SQLAlchemyError:
            self.handle_db_err(err, res, req)
        else:
            js_query['page'] = page + 1
            self.handle_res(res, req, resp, query=js_query)

    @staticmethod
    def author_filter(auth):
        return models.Podcast.author.like('{}%'.format(auth))

    @staticmethod
    def title_filter(title):
        return models.Podcast.title.like('{}%'.format(title))

    @staticmethod
    def dow_filter(dow):
        return models.Podcast.published_on_week_day(dow) >= 2

    @staticmethod
    def dom_filter(dom):
        return models.Podcast.published_on_month_day(dom) >= 2

    @staticmethod
    def category_filter(cat_name):
        return models.Podcast.categories.any(models.Category.name == cat_name)

    @staticmethod
    def published_since_filter(date_str):
        parsed = datetime.strptime(date_str, '%Y-%m-%d')
        return models.Podcast.published_since(parsed)

