from resources import SearchResource, PodcastResource,


ROUTES = {'/search/{model}': SearchResource()
          '/podcast/{id}': PodcastResource(),
          '/podcast/{id}/{subcoll}': PodcastSubcollResource(),
