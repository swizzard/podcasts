import json

import falcon

import models
from base import DBResource
from helpers import Noncer

class LoginResource(DBResource):
    def __init__(self):
        super().__init__()
        self.noncer = Noncer()

    def handle_bad_login(self):
        raise falcon.HTTPBadRequest('Invalid login attempt')

    def on_post(self, req, resp):
        try:
            body = json.load(req.stream)
        except (TypeError, ValueError):
            self.handle_bad_login()
        else:
            try:
                username = body['username']
                pwd = body['password']
            except KeyError:
                self.handle_bad_login()
            else:
                user = self.session.query(models.User).filter_by(
                    name=username).one_or_none()
                if user is None:
                    self.handle_bad_login()
                else:
                    if user.password == pwd:
                        nonce = noncer.get_token(username)
                        msg = {'token': nonce,
                               'expiration': nonce.expiration}
                        resp.body = json.dumps(msg)
                    else:
                        self.handle_bad_login()

