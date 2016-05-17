import json

from sqlalchemy import select, exists, func
from sqlalchemy import UniqueConstraint, create_engine, orm, schema, types
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import object_session
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy_utils.types.password import PasswordType


with open('config.json') as f:
    cfg = json.load(f)


conn_str = 'mysql+pymysql://{username}:{password}@{host}/{dbname}'.format(
        username=cfg['user'], password=cfg['password'], host=cfg['address'],
        dbname=cfg['db_name'])


engine = create_engine(conn_str + '?charset=utf8mb4', convert_unicode=True,
                       echo=bool(cfg['echo']))


Base = declarative_base(bind=engine)


categories_to_podcasts = schema.Table('categories_to_podcasts', Base.metadata,
                                      schema.Column('id', types.Integer,
                                                    primary_key=True),
                                      schema.Column('category_id', types.Integer,
                                                    schema.ForeignKey('categories.id')),
                                      schema.Column('podcast_id', types.Integer,
                                                    schema.ForeignKey('podcasts.id')))

users_to_likes = schema.Table('users_to_podcasts_likes', Base.metadata,
                              schema.Column('id', types.BigInteger,
                                            primary_key=True),
                              schema.Column('podcast_id', types.Integer,
                                            schema.ForeignKey('podcasts.id')),
                              schema.Column('user_id', types.Integer,
                                            schema.ForeignKey('users.id')))


class Category(Base):
    __tablename__ = 'categories'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.String(255), unique=True, index=True)


class Podcast(Base):
    __tablename__ = 'podcasts'

    id = schema.Column(types.Integer, primary_key=True)
    title = schema.Column(types.Text(collation='utf8mb4_general_ci'))
    feed_url = schema.Column(types.String(255), unique=True, nullable=False)
    language = schema.Column(types.String(100), default='English')
    author = schema.Column(types.Text(collation='utf8mb4_general_ci'))
    explicit = schema.Column(types.Boolean)
    homepage = schema.Column(types.String(255))
    summary = schema.Column(types.Text(collation='utf8mb4_general_ci')) 

    categories = orm.relationship('Category', secondary='categories_to_podcasts',
                                  backref='podcasts')
    episodes = orm.relationship('Episode', backref='podcast')
    likers = orm.relationship('User', secondary='users_to_podcasts_likes',
                               back_populates='likes',
                               lazy='dynamic')

    def __repr__(self):
        return '<Podcast: {}>'.format(self.title)

    @hybrid_property
    def episode_count(self):
        return len(self.episodes)

    @hybrid_property
    def days_of_month(self):
        return [ep.day_of_month for ep in self.episodes]

    @hybrid_method
    def published_on_month_day(self, day_of_month):
        return len([day for day in self.days_of_month if day == day_of_month])

    @published_on_month_day.expression
    def published_on_month_day(cls, week_day):
        return select([func.count(Episode.id)]).where(
            Episode.podcast_id == cls.id).where(
            Episode.day_of_month == week_day).label(
            'published_on_month_day')

    @hybrid_property
    def week_days(self):
        return [ep.week_day for ep in self.episodes]

    @hybrid_method
    def published_on_week_day(self, week_day):
        return len([day for day in self.week_days if day == week_day])

    @published_on_week_day.expression
    def published_on_week_day(cls, week_day):
        return select([func.count(Episode.id)]).where(
            Episode.podcast_id == cls.id).where(
            Episode.week_day == week_day).label(
            'published_on_week_day')

    @hybrid_property
    def durations(self):
        return [ep.duration for ep in self.episodes]

    @hybrid_method
    def longer_than(self, comp_dur):
        return len([dur for dur in self.durations if dur > comp_dur])

    @longer_than.expression
    def longer_than(cls, comp_dur):
        return select([func.count(Episode.id)]).where(
            Episode.podcast_id == cls.id).where(
            Episode.duration > comp_dur).label(
            'longer_than')

    @hybrid_property
    def last_published(self):
        return max(ep.date for ep in self.episodes)

    @hybrid_method
    def published_since(self, comp_date):
        return self.last_published >= comp_date

    @published_since.expression
    def published_since(cls, comp_date):
        return select([func.count(Episode.id)]).where(
            Episode.podcast_id == cls.id).where(
            Episode.date >= comp_date).label('pubd')


class Episode(Base):
    __tablename__ = 'episodes'
    __table_args__ = (UniqueConstraint('title', 'podcast_id', 'date',
                                       name='unique_ep'),)

    id = schema.Column(types.Integer, primary_key=True)
    duration = schema.Column(types.Integer)
    title = schema.Column(types.String(191, collation='utf8mb4_general_ci'))
    description = schema.Column(types.Text(collation='utf8mb4_general_ci'))
    podcast_id = schema.Column(types.Integer, schema.ForeignKey('podcasts.id'))
    week_day = schema.Column(types.Integer)
    day_of_month = schema.Column(types.Integer)
    date = schema.Column(types.DateTime)

    def __repr__(self):
        return '<Episode: {} ({})>'.format(self.title, self.podcast_id)


class User(Base):
    __tablename__ = 'users'

    id = schema.Column(types.Integer, primary_key=True)
    name = schema.Column(types.String(191, collation='utf8mb4_general_ci'),
                         unique=True, nullable=False, index=True)
    password = schema.Column(PasswordType(schemes=['pbkdf2_sha512']),
                             unique=True, nullable=False)
    email = schema.Column(types.String(255), unique=True, nullable=True,
                          index=True)
    public = schema.Column(types.Boolean)

    likes = orm.relationship('Podcast', secondary='users_to_podcasts_likes',
                             back_populates='likers', lazy='dynamic')

    def __repr__(self):
        return '<User: {} ({})>'.format(self.name, self.email)



Session = scoped_session(orm.sessionmaker(bind=engine))
Base.metadata.create_all(checkfirst=True)

