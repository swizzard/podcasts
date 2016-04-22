import falcon

from api import resources


ROUTES = {
    '/search/podcasts': resources.SearchResource(),
    '/categories/{category_id}': resources.CategoryResource(),
    '/podcasts/{podcast_id}': resources.PodcastResource(),
    '/podcasts/{podcast_id}/{rel_type}': resources.PodcastUsersResource(),
    '/podcasts/{podcast_id}/categories': resources.PodcastCategoriesResource(),
    '/users/{user_id}': resources.UserResource(),
    '/users/{user_id}/podcasts/{rel_type}': resources.UserPodcastsResource(),
    '/users/{user_id}/podcasts/{rel_type}/{podcast_id}':
        resources.UserPodcastsResource(),
    '/login': resources.LoginResource()
    }


def create_api():
    api = falcon.API()
    for route, res in ROUTES.items():
        try:
            api.add_route(route, res)
        except ValueError:
            print(route, res)
            raise
    return api


app = create_api()

