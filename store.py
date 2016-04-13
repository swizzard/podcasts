import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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
        cats = []
        if categories:
            cats = self.session.query(models.Category).filter(
                models.Category.name.in_(categories)).all()
            to_add = categories - {cat.name for cat in cats}
            for cat_name in to_add:
                new_cat = self.safe_commit(models.Category(
                    name=cat_name))
                if new_cat:
                    cats.append(new_cat)
        return cats

    def get_episodes(self, episodes, pod_id):
        out = []
        for ep in episodes:
            episode = self.session.query(models.Episode).filter(
                models.Episode.podcast_id == pod_id,
                models.Episode.title == ep['title'],
                models.Episode.date == ep['date'],
                ).one_or_none()
            if episode is None:
                new_episode = models.Episode(podcast_id=pod_id,
                                             duration=ep['duration'],
                                             title=ep['title'],
                                             description=ep['description'],
                                             week_day=ep['week_day'],
                                             day_of_month=ep['day_of_month'],
                                             date=ep['date'])
                episode = self.safe_commit(new_episode)
            if episode is not None:
                out.append(episode)
        return out

    def safe_commit(self, obj):
        try:
            self.session.add(obj)
            self.session.commit()
            logging.info('{}'.format(obj))
        except SQLAlchemyError as err:
            import pdb
            pdb.set_trace()
            logging.exception('{}'.format(obj))
            self.session.rollback()
        else:
            return obj

