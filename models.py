import json

from sqlalchemy import UniqueConstraint, create_engine, orm, schema, types
from sqlalchemy.dialects.mysql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
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


users_to_dislikes = schema.Table('users_to_podcasts_dislikes', Base.metadata,
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

    week_days = orm.relationship('WeekDay', secondary='week_days_to_podcasts')
    days_of_month = orm.relationship('DayOfMonth',
                                     secondary='days_of_month_to_podcasts')
    categories = orm.relationship('Category', secondary='categories_to_podcasts')
    episodes = orm.relationship('Episode', backref='podcast')
    likers = orm.relationship('User', secondary='users_to_podcasts_likes',
                              backref='likes')
    dislikers = orm.relationship('User', secondary='users_to_podcasts_dislikes',
                                 backref='dislikes')

    def __repr__(self):
        return '<Podcast: {}>'.format(self.title)

    @hybrid_property
    def episode_count(self):
        return len(self.episodes)

    @hybrid_property
    def days_of_month(self):
        return [ep.day_of_month for ep in self.episodes]

    @hybrid_property
    def week_days(self):
        return [ep.week_day for ep in self.episodes]

    @hybrid_property
    def durations(self):
        return [ep.duration for ep in self.episodes]

    @hybrid_property
    def likers(self):
        return [user for user in self.likers if user.public]

    @hybrid_property
    def dislikers(self):
        return [user for user in self.dislikers if user.public]


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

    def __repr__(self):
        return '<User: {} ({})>'.format(name, email)


Session = orm.sessionmaker(bind=engine)
Base.metadata.create_all(checkfirst=True)

