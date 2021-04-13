import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Anecdotiy(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Anecdotiy'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('Users.id'))
    rating = sqlalchemy.Column(sqlalchemy.Integer)
    likes_and_dislikes = sqlalchemy.Column(sqlalchemy.String)

    leader = orm.relation('User')
    categories = orm.relation("Genre",
                              secondary="association",
                              backref="Anecdotiy")

    def __repr__(self):
        return f'<Job> {self.job}'
