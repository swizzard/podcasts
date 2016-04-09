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
        podcast = self.safe_commit(podcast)
        if podcast is not None:
            podcast.categories = self.get_categories(pod_info['categories'])
            podcast.episodes = self.get_episodes(pod_info['episodes'], podcast.id)
            self.safe_commit(podcast)

    def get_categories(self, categories):
        cats = self.session.query(models.Category).filter(
            models.Category.name.in_(categories)).all()
        to_add = categories - {cat.name for cat in cats}
        for cat_name in to_add:
            new_cat = self.safe_commit(models.Category(name=cat_name))
            if new_cat:
                cats.append(new_cat)
        return cats

    def get_episodes(self, episodes, pod_id):
        out = []
        for ep in episodes:
            episode = self.session.query(models.Episode).filter(
                models.Episode.podcast_id == pod_id,
                models.Episode.title == ep['title'],
                models.Episode.day_of_month == ep['date'],
                ).one_or_none() or self.safe_commit(models.Episode(**ep))
            if episode is not None:
                out.append(episode)
        return out

    def safe_commit(self, obj):
        try:
            self.session.add(obj)
            self.session.commit()
        except SQLAlchemyError:
            logging.exception(u'%s', obj)
            self.session.rollback()
        else:
            return obj


class DummyStorage():
    def __init__(self):
        pass

    @staticmethod
    def store_podcast(pod_info):
        return pod_info

