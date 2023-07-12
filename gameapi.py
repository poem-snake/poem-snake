from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from models import db, User, Record
from sqlalchemy import desc, func
import os
from api import gravatar

gameapi = Blueprint('gameapi', __name__, url_prefix='/api')


@gameapi.route('/users')
def get_users():
    return jsonify([User.query.filter_by(id=u).first().info() for u in current_app.users])


@gameapi.route('/history')
def history():
    last = request.args.get('last', 19260817, type=int)
    records = Record.query.filter(Record.id < last).order_by(
        desc(Record.id)).limit(10).all()
    return jsonify([r.info() for r in records])


@gameapi.route('/ranklist')
def ranklist():
    perpage = request.args.get('perpage', 10, type=int)
    page = request.args.get('page', 1, type=int)
    users = User.query.join(Record, Record.user_id == User.id).with_entities(User.id, func.count(Record.id)) \
        .group_by(User.id).order_by(desc(func.count(Record.id))).paginate(page, perpage, False)
    first = (page - 1) * perpage + 1
    data = []
    for i in users.items:
        u = User.query.filter_by(id=i[0]).first().info()
        u['count'] = i[1]
        data.append(u)
    return jsonify({'page': page, "perpage": perpage, 'data': [
        {"num": first + idx, "uid": u['id'], "username": u['username'], 'count': u['count'],
         'gravatar': u['gravatar']} for
        idx, u in enumerate(data)]})


@gameapi.route('/coin')
@login_required
def coin():
    return jsonify({'coin': current_user.get_coin()})


@gameapi.route('/skipcheck')
@login_required
def skipcheck():
    if current_user.admin or current_user.get_coin() >= 50:
        return jsonify(True)
    else:
        return jsonify(False)


@gameapi.route('/upload', methods=['POST'])
def upload_avatar():
    class AvatarForm(FlaskForm):
        avatar = FileField(validators=[FileRequired(), FileAllowed(['png', 'jpg'], 'Images only!')])

    form = AvatarForm(meta={'csrf': False})
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return jsonify({'status': 'error', 'message': '请先登录'})
        filename = str(current_user.id) + '.png'
        try:
            form.avatar.data.save(os.path.join('./static/avatars/', filename))
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        current_user.avatar_uploaded = False
        db.session.commit()
        return jsonify({'status': 'success', 'message': '上传成功'})
    else:
        return jsonify({'status': 'error', 'message': form.errors})
