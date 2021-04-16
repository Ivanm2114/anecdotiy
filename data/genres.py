import sqlalchemy
from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table(
    'association',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('Anecdotiy', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('Anecdotiy.id')),
    sqlalchemy.Column('Genre', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('Genre.id'))
)


class Genre(SqlAlchemyBase):
    __tablename__ = 'Genre'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
