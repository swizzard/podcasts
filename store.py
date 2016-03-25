import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

import models


class Storage():
    def __init__(self):
        self.session = models.Session()

    def store_podcast(self, pod_info):
        link = pod_info['link']
        podcast = self.session.query(models.Podcast).filter_by(
            feed_url=link).one_or_none() or models.Podcast()
        podcast.feed_url = link
        podcast.language = pod_info['language']
        podcast.author = pod_info['author']
        podcast.title = pod_info['title']
        podcast.summary = pod_info['summary']
        podcast.explicit = pod_info['explicit']
        podcast.duration = pod_info['expected_dur']
        podcast.categories = get_categories(session, pod_info['categories'])
        try:
            self.session.add(podcast)
            self.session.commit()
        except SQLAlchemyError:
            logging.exception('error storing podcast %s', link)
            self.session.rollback()
        else:
            logging.info('stored %s', podcast.title)

    def get_categories(session, categories):
        cats = self.session.query(models.Category).filter(Category.name.in_(
            categories)).all()
        to_add = categories - {cat.name for cat in cats}
        for cat_name in to_add:
            new_cat = models.Category(name=cat_name)
            self.session.add(new_cat)
            try:
                self.session.commit()
            except SQLAlchemyError:
                logging.exception('error adding category %s', cat_name)
                self.session.reset()
            else:
                cats.append(new_cat)
        return cats


class DummyStorage():
    def __init__(self):
        pass

    @staticmethod
    def store_podcast(pod_info):
        return pod_info

