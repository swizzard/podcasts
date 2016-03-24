import json

from sqlalchemy import create_engine, orm, schema, types
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.ext.declarative import declarative_base


with open('config.json') as f:
    cfg = json.load(f)


conn_str = 'mysql+pymysql://{username}:{password}@{host}/{dbname}'.format(
        username=cfg['user'], password=cfg['password'], host=cfg['address'],
        dbname=cfg['db_name'])


engine = create_engine(conn_str + '?charset=utf8', echo=bool(cfg['echo']))


Base = declarative_base(bind=engine)


class WeekDay(Base):
    __tablename__ = 'weekday'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday',
                              'Thursday', 'Friday', 'Saturday'),
                         unique=True, index=True)


class DayOfMonth(Base):
    __tablename__ = 'day_of_month'

    id = schema.Column(types.Integer, primary_key=True)
    day = schema.Column(types.Integer, unique=True, index=True)


week_days_to_podcasts = schema.Table('week_days_to_podcasts', Base.metadata,
                                     schema.Column('id', types.Integer,
                                                   primary_key=True),
                                     schema.Column('week_day_id',
                                                   types.Integer,
                                                   schema.ForeignKey('weekday.id')),
                                     schema.Column('podcast_id',
                                                   types.Integer,
                                                   schema.ForeignKey('podcasts.id')))


days_of_month_to_podcasts = schema.Table('days_of_month_to_podcasts', Base.metadata,
                                         schema.Column('id', types.Integer,
                                                       primary_key=True),
                                         schema.Column('day_of_month_id',
                                                       types.Integer,
                                                       schema.ForeignKey('day_of_month.id')),
                                         schema.Column('podcast_id',
                                                       types.Integer,
                                                       schema.ForeignKey('podcasts.id')))


categories_to_podcasts = schema.Table('categories_to_podcasts', Base.metadata,
                                      schema.Column('id', types.Integer,
                                                    primary_key=True),
                                      schema.Column('category_id', types.Integer,
                                                    schema.ForeignKey('categories.id')),
                                      schema.Column('podcast_id', types.Integer,
                                                    schema.ForeignKey('podcasts.id')))
 

class Category(Base):
    __tablename__ = 'categories'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.String(255), unique=True, index=True)


class Podcast(Base):
    __tablename__ = 'podcasts'

    id = schema.Column(types.Integer, primary_key=True)
    title = schema.Column(types.String(255, collation='utf8_general_ci'))
    feed_url = schema.Column(types.String(255), unique=True, nullable=False)
    duration = schema.Column(types.String(255), index=True, nullable=True)
    language = schema.Column(types.String(100), default='English')
    explicit = schema.Column(types.Boolean)
    summary = schema.Column(types.Text(collation='utf8_general_ci')) 

    week_days = orm.relationship('WeekDay', secondary='week_days_to_podcasts')
    days_of_month = orm.relationship('DayOfMonth',
                                     secondary='days_of_month_to_podcasts')
    categories = orm.relationship('Category', secondary='categories_to_podcasts')


Session = orm.sessionmaker(bind=engine)
Base.metadata.create_all(checkfirst=True)

