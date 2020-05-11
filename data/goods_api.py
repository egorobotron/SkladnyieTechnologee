import flask
from . import db_session
from flask import jsonify, request
from data.goods import Goods
blueprint = flask.Blueprint('goods_api', __name__,
                            template_folder='templates')


@blueprint.route('/api/goods')
def get_goods():
    session = db_session.create_session()
    goods = session.query(Goods).all()
    return jsonify(
        {
            'goods':
                [item.to_dict(only=('name', 'content', 'user.name'))
                 for item in goods]
        }
    )

@blueprint.route('/api/goods/<int:goods_id>',  methods=['GET'])
def get_one_goods(goods_id):
    session = db_session.create_session()
    goods = session.query(Goods).get(goods_id)
    if not goods:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'goods': goods.to_dict(only=('name', 'content', 'user_id', 'is_fragile'))
        }
    )

@blueprint.route('/api/goods', methods=['POST'])
def create_goods():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'content', 'user_id', 'is_fragile']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    goods = Goods(
        name=request.json['name'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_fragile'],
    )
    session.add(goods)
    session.commit()
    return jsonify({'success': 'OK'})

@blueprint.route('/api/goods/<int:goods_id>', methods=['DELETE'])
def delete_goods(goods_id):
    session = db_session.create_session()
    goods = session.query(Goods).get(goods_id)
    if not goods:
        return jsonify({'error': 'Not found'})
    session.delete(goods)
    session.commit()
    return jsonify({'success': 'OK'})