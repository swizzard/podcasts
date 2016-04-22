import json
import logging

import falcon
from sqlalchemy.exc import SQLAlchemyError

import models
from api.resources.base import DBResource
from api.resources.helpers import Validator, Paginator, validate_rel_type

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
                        raise falcon.HTTPConflict(
                            'User {} already exists'.format(username))
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

    def on_get(self, req, resp, user_id, rel_type):
        validate_rel_type(rel_type)
        try:
            public, name = self.session.query(models.User.public,
                                              models.User.name).filter_by(
                id=user_id).one()
        except NoResultFound:
            self.handle_one(obj, req, resp)
        else:
            filts = {
                'likes': models.Podcast.liking_users.any(
                    models.User.id == user_id),
                'dislikes': models.Podcast.disliking_users.any(
                    models.User.id == user_id)
                }
            if self.validator.can_view(public, name, user_id, req):
                query = self.session.query(models.Podcast).filter(filts[rel_type]) 
                try:
                    pagination, res = self.paginator.paginate(req, query)
                except SQLAlchemyError as err:
                    self.handle_db_err(err, req, resp)
                else:
                    self.handle_res(res, req, resp, models.Podcast,
                                    pagination=pagination)

    def on_put(self, req, resp, user_id, rel_type, podcast_id):
        validate_rel_type(rel_type)
        user = self.session.query(models.User).get(user_id)
        if user is None:
            raise falcon.HTTPNotFound('No such user')
        elif not self.validator.validate(user.name, user_id, req):
            raise falcon.HTTPUnauthorized('Invalid credentials')
        else:
            podcast = self.session.query(models.Podcast).get(podcast_id)
            if podcast is None:
                raise falcon.HTTPNotFound('No such podcast') 
            else:
                getattr(user, rel_type).append(podcast)
                self.session.add(user)
                try:
                    self.session.commit()
                except SQLAlchemyError as err:
                    self.handle_db_err(err, req, resp)
                else:
                    resp_body = {'user_id': user_id, 'podcast_id': podcast_id,
                                 'added_to': rel_type, 'success': True}
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
                                 'token': token}
                    self.handle_one(auth_resp, req, resp)
                else:
                    self.handle_bad_login()
            except SQLAlchemyError as err:
                self.handle_db_err(err, req, resp)

    def handle_bad_login(self):
        raise falcon.HTTPBadRequest('Invalid login attempt',
                                    'Invalid login attempt')

