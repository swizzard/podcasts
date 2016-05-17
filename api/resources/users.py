import json
import logging

import falcon
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

import models
from api.resources.base import DBResource
from api.resources.helpers import Validator, Paginator

class UserResource(DBResource):

    def __init__(self):
        super().__init__(models.User)
        self.validator = Validator()

    def on_post(self, req, resp, user_id=None):
        try:
            body = json.loads(req.stream.read().decode('utf8'))
        except (AttributeError, TypeError, ValueError):
            logging.exception('err:')
            raise falcon.HTTPNotAcceptable('POST body must be JSON')
        else:
            try:
                username = body['username']
                password = body['password']
                email = body['email']
                public = bool(body['public'])
            except KeyError as err:
                missing_key = err.args[0]
                raise falcon.HTTPBadRequest('Invalid User',
                                            '{} is missing'.format(missing_key))
            else:
                try:
                    new_user = models.User(name=username, password=password,
                                           email=email, public=public)
                    self.session.add(new_user)
                    self.session.commit()
                except IntegrityError as ierr:
                    self.session.rollback()
                    if ierr.orig.args[0] == 1062:
                        err = {
                            'title': 'User exists',
                            'description': 'User {} already exists'.format(username)
                        }
                        raise falcon.HTTPConflict(**err)
                    else:
                        self.handle_db_err(ierr, req, resp)
                except SQLAlchemyError as err:
                    self.handle_db_err(err, req, resp)
                else:
                    resp.status = falcon.HTTP_201
                    self.handle_one(new_user, req, resp)

    def on_get(self, req, resp, user_id):
        user = self.session.query(models.User).get(user_id)
        if self.validator.can_view(user.public, user.name, user_id, req):
            return self.handle_one(user, req, resp)
        else:
            raise falcon.HTTPForbidden('User is private')


class UserPodcastsResource(DBResource):
    def __init__(self):
        super().__init__(models.User)
        self.validator = Validator()
        self.paginator = Paginator()

    def on_get(self, req, resp, user_id):
        try:
            public, name = self.session.query(models.User.public, models.User.name
                ).filter_by(id=user_id).one()
        except NoResultFound:
            self.handle_one(obj, req, resp)
        else:
            user = self.session.query(models.User).get(user_id)
            if self.validator.can_view(public, name, user_id, req):
                user = self.session.query(models.User).get(user_id).likes
                try:
                    pagination, res = self.paginator.paginate(req, query)
                except SQLAlchemyError as err:
                    self.handle_db_err(err, req, resp)
                else:
                    self.handle_res(res, req, resp, models.Podcast,
                                    pagination=pagination)
            else:
                raise falcon.HTTPUnauthorized()

    def get_user_podcast(self, user_id, podcast_id, req):
        user = self.session.query(models.User).get(user_id)
        if user is None:
            raise falcon.HTTPNotFound('No such user', 'No such user')
        elif not self.validator.validate(user.name, user_id, req):
            raise falcon.HTTPUnauthorized('Invalid credentials',
                                          'Invalid credentials')
        else:
            podcast = self.session.query(models.Podcast).get(podcast_id)
            if podcast is None:
                raise falcon.HTTPNotFound('No such podcast')
            else:
                return user, podcast

    def on_put(self, req, resp, user_id, podcast_id):
        user, podcast = self.get_user_podcast(user_id, podcast_id, req)
        user.likes.append(podcast)
        self.session.add(user)
        try:
            self.session.commit()
        except SQLAlchemyError as err:
            self.handle_db_err(err, req, resp)
        else:
            resp_body = {'user_id': user_id,
                         'podcast_id': podcast_id,
                         'action': 'added',
                         'success': True}
            self.handle_one(resp_body, req, resp)

    def on_delete(self, req, resp, user_id, podcast_id):
        user, podcast = self.get_user_podcast(user_id, podcast_id, req)
        res = user.likes
        for podcast in res:
            if podcast.id == podcast_id:
                res.remove(podcast)
                break
        self.session.add(user)
        try:
            self.session.commit()
        except SQLAlchemyError as err:
            self.handle_db_err(err, req, resp)
        else:
            resp_body = {'user_id': user_id,
                         'podcast_id': podcast_id,
                         'action': 'deleted',
                         'success': True}
            self.handle_one(resp_body, req, resp)


class LoginResource(DBResource):
    def __init__(self):
        super().__init__(models.User)
        self.validator = Validator()

    def on_post(self, req, resp):
        try:
            body = json.loads(req.stream.read().decode('utf8'))
            username = body['username']
            password = body['password']
        except (AttributeError, KeyError, TypeError, ValueError):
            self.handle_bad_login()
        else:
            try:
                user = self.session.query(models.User).filter_by(
                    name=username).one_or_none()
                if user and (password == user.password):
                    token = self.validator.noncer.get_token(username)
                    auth_resp = {'username': username,
                                 'token': token,
                                 'userId': user.id}
                    self.handle_one(auth_resp, req, resp)
                else:
                    self.handle_bad_login()
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, resp)

    def handle_bad_login(self):
        msg = 'Invalid login attempt'
        raise falcon.HTTPBadRequest(msg, msg)

