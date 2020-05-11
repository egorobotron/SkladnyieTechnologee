import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Goods(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_fragile = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    expired_time = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=(datetime.datetime.now() + datetime.timedelta(days=365)))
    place_come = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    place_going = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __repr__(self):
        return '<Goods> ' + str(self.id) + ' ' + self.name + ' ' + self.content
