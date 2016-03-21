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


week_days_to_schedule = schema.Table('week_days_to_schedule', Base.metadata,
                                     schema.Column('id', types.Integer,
                                                   primary_key=True),
                                     schema.Column('week_day_id',
                                                   types.Integer,
                                                   schema.ForeignKey('weekday.id')),
                                     schema.Column('schedule_id',
                                                   types.Integer,
                                                   schema.ForeignKey('schedules.id')))


day_of_month_to_schedule = schema.Table('day_of_month_to_schedule', Base.metadata,
                                        schema.Column('id', types.Integer,
                                                      primary_key=True),
                                        schema.Column('day_of_month_id',
                                                      types.Integer,
                                                      schema.ForeignKey('day_of_month.id')),
                                        schema.Column('schedule_id',
                                                      types.Integer,
                                                      schema.ForeignKey('schedules.id')))


schedule_to_podcasts = schema.Table('schedules_to_podcasts', Base.metadata,
                                    schema.Column('id', types.Integer,
                                                  primary_key=True),
                                    schema.Column('schedule_id', types.Integer,
                                                  schema.ForeignKey('schedules.id')),
                                    schema.Column('podcast_id', types.Integer,
                                                  schema.ForeignKey('podcasts.id')))

class Category(Base):
    __tablename__ = 'categories'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.String(255), unique=True, index=True)


categories_to_podcast = schema.Table('categories_to_podcasts', Base.metadata,
                                     schema.Column('id', types.Integer,
                                                   primary_key=True),
                                     schema.Column('category_id', types.Integer,
                                                   schema.ForeignKey('categories.id')),
                                     schema.Column('podcast_id', types.Integer,
                                                   schema.ForeignKey('podcasts.id')))
 

class Schedule(Base):
    __tablename__ = 'schedules'

    id = schema.Column(types.Integer, primary_key=True)
    alias = schema.Column(types.String(255), unique=True)

    week_days = orm.relationship('WeekDay', secondary='week_days_to_schedule')
    days_of_month = orm.relationship('DayOfMonth',
                                     secondary='day_of_month_to_schedule')


class Podcast(Base):
    __tablename__ = 'podcasts'

    id = schema.Column(types.Integer, primary_key=True)
    title = schema.Column(types.String(255, collation='utf8_general_ci'))
    feed_url = schema.Column(types.String(255), unique=True, nullable=False)
    duration = schema.Column(types.String(255), index=True, nullable=True)
    language = schema.Column(types.String(100), default='English')
    explicit = schema.Column(types.Boolean)
    summary = schema.Column(types.Text(collation='utf8_general_ci')) 
    schedule_id = schema.Column(types.Integer, schema.ForeignKey('schedules.id'))

    schedule = orm.relationship('Schedule')
    categories = orm.relationship('Category', secondary='categories_to_podcasts')


Session = orm.sessionmaker(bind=engine)
Base.metadata.create_all(checkfirst=True)

