import hashlib

import falcon

from models import User
from noncer import Noncer


class User():
    def __init__(self):
        self.noncer = Noncer
        self.token_header = 'X-Auth-Token'
        self.user_header = 'X-Auth-User'

    def token_valid(self, req):
        try:
            username = req.headers[self.user_header]
            token = req.headers[self.token_header]
        except KeyError as err:
            raise falcon.HTTPMissingHeader(err.args[0])
        else:
            return self.noncer.validate_token(username, token)

    def before(self, req, resp, resource, params):
        if not self.token_valid(req):
            raise falcon.HTTPUnauthorized('Invalid or expired API token',
                                          'The provided API token is invalid'
                                          'or expired')

    def after(self, req, resp, resource):
        if resource.
