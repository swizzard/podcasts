from functools import partial
import json

import falcon

import models
from api.resources.helpers import DBEncoder

class DBResource():
    session = None

    def __init__(self, model):
        if DBResource.session is None:
            DBResource.session = models.Session()
        self.model = model
        self.dumps = partial(json.dumps, cls=DBEncoder)

    def handle_db_err(self, err, req, resp):
        resp.status = falcon.HTTP_500
        resp.body = self.dumps({'path': req.path,
                                'err': err.__class__.__name__,
                                'args': err.args})
        self.session.rollback()

    def handle_res(self, objs, req, resp, model=None, **body_kwargs):
        model = model if model is not None else self.model
        objs = objs if objs is not None else []
        out = {'path': req.path,
               'model': model.__name__,
               'result': objs}
        out.update(body_kwargs)
        resp.append_header('Access-Control-Allow-Origin', '*')
        resp.body = self.dumps(out)

    def handle_one(self, obj, req, resp, **body_kwargs):
        if obj is None:
            resp.append_header('Access-Control-Allow-Origin', '*')
            raise falcon.HTTPNotFound()
        else:
            obj = [obj] if obj is not None else []
            self.handle_res(obj, req, resp, **body_kwargs)

