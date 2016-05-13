import json

from sqlalchemy.exc import SQLAlchemyError

from models import Podcast, Category
from api.resources.base import DBResource



class AuthorsAutocompleteResource(DBResource):
    results = []

    def __init__(self):
        super().__init__(Podcast)

    def on_get(self, req, resp):
        if not self.results:
            try:
                res = self.session.query(Podcast.author).group_by().all()
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, res)
            else:
                self.results = [auth[0] for auth in res]
        return self.handle_res(self.results, req, resp)


class CategoriesAutocompleteResource(DBResource):
    results = []

    def __init__(self):
        super().__init__(Category)

    def on_get(self, req, resp):
        if not self.results:
            try:
                res = self.session.query(Category.name).all()
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, res)
            else:
                self.results = [cat[0] for cat in res]
        return self.handle_res(self.results, req, resp)

