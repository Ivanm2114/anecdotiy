import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Compilation(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Compilation'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    anecdoties = sqlalchemy.Column(sqlalchemy.String)
