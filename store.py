import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

import models


def store_podcast(session, pod_info):
    link = pod_info['link']
    podcast = session.query(models.Podcast).filter_by(
        feed_url=link).one_or_none() or models.Podcast()
    podcast.feed_url = link
    podcast.language = pod_info['language']
    podcast.author = pod_info['author']
    podcast.title = pod_info['title']
    podcast.summary = pod_info['summary']
    podcast.explicit = pod_info['explicit']
    podcast.duration = pod_info['expected_dur']
    podcast.categories = get_categories(session, pod_info['categories'])
    podcast.schedule = get_schedule(session, pod_info)
    try:
        session.add(podcast)
        session.commit()
    except SQLAlchemyError:
        logging.exception('error storing podcast %s', link)
        session.rollback()


def get_categories(session, categories):
    cats = session.query(models.Category).filter(Category.name.in_(
        categories)).all()
    to_add = categories - {cat.name for cat in cats}
    for cat_name in to_add:
        new_cat = models.Category(name=cat_name)
        session.add(new_cat)
        try:
            session.commit()
        except SQLAlchemyError:
            logging.exception('error adding category %s', cat_name)
            session.reset()
        else:
            cats.append(new_cat)
    return cats



