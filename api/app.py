import logging

import falcon
from falcon_cors import CORS

from api import resources
from api.middleware import LoggingMiddleware


logging.basicConfig(level=logging.INFO)

ROUTES = {
    '/search/podcasts': resources.SearchResource(),
    '/categories/{category_id}': resources.CategoryResource(),
    '/podcasts/{podcast_id}': resources.PodcastResource(),
    '/podcasts/{podcast_id}/likers': resources.PodcastUsersResource(),
    '/podcasts/{podcast_id}/categories': resources.PodcastCategoriesResource(),
    '/users': resources.UserResource(),
    '/users/{user_id}': resources.UserResource(),
    '/users/{user_id}/likes': resources.UserPodcastsResource(),
    '/users/{user_id}/likes/{podcast_id}': resources.UserPodcastsResource(),
    '/login': resources.LoginResource(),
    '/autocomplete/author': resources.AuthorsAutocompleteResource(),
    '/autocomplete/category': resources.CategoriesAutocompleteResource()
    }


def create_api(middleware):
    api = falcon.API(middleware=middleware)
    for route, res in ROUTES.items():
        api.add_route(route, res)
    return api


cors = CORS(allow_all_origins=True,
            allow_headers_list=['x-auth-user', 'x-auth-token', 'accept',
                                'content-type'],
            allow_methods_list=['POST', 'OPTIONS', 'DELETE', 'PUT', 'GET'])
app = create_api(middleware=[LoggingMiddleware(), cors.middleware])

