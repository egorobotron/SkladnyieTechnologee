from flask_restful import Resource, abort, reqparse
from . import db_session
from data.goods import Goods
from flask import jsonify, request


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    goods = session.query(Goods).get(news_id)
    if not goods:
        abort(404, message=f"News {news_id} not found")

class GoodsResource(Resource):
    def get(self, goods_id):
        abort_if_news_not_found(goods_id)
        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)
        return jsonify({'news': goods.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, goods_id):
        abort_if_news_not_found(goods_id)
        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)
        session.delete(goods)
        session.commit()
        return jsonify({'success': 'OK'})

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_fragile', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)

class GoodsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        goods = session.query(Goods).all()
        return jsonify({'goods': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in goods]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        goods = Goods(
            name=args['name'],
            content=args['content'],
            user_id=args['user_id'],
            is_fragile=args['is_fragile']
        )
        session.add(goods)
        session.commit()
        return jsonify({'success': 'OK'})