import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Anecdotiy(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Anecdotiy'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('Users.id'))
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    users_likes = sqlalchemy.Column(sqlalchemy.String, default='')
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    users_dislikes = sqlalchemy.Column(sqlalchemy.String, default='')

    creator = orm.relation('User')
    categories = orm.relation("Genre",
                              secondary="association",
                              backref="Anecdotiy")

    def __repr__(self):
        return f'<Anecdot> {self.id}'
