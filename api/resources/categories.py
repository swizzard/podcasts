from sqlalchemy.exc import SQLAlchemyError

import models
from api.resources.base import DBResource
from api.resources.helpers import Paginator


class CategoryResource(DBResource):
    def __init__(self):
        super().__init__(models.Category)
        self.paginator = Paginator()

    def on_get(self, req, resp, category_id=None):
        print(category_id)
        if category_id != 'undefined':
            category = self.session.query(models.Category).get(category_id)
            self.handle_one(category, req, resp)
        else:
            query = self.session.query(models.Category)
            try:
                pagination, res = self.paginator.paginate(req, query)
            except SQAlchemyError as err:
                self.handle_db_err(err, req, resp)
            else:
                self.handle_res(res, req, resp, pagination=pagination)

