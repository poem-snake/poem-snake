from flask import current_app
from flask_login import current_user, login_required
from flask_socketio import emit, SocketIO
from models import *
from sqlalchemy import desc
import json
import api

socket_io = SocketIO(logger=True, engineio_logger=True, cors_allowed_origins="*")


@socket_io.on('connect')
def connect():
    if current_user.is_authenticated:
        current_app.users.append(current_user.id)
    if not hasattr(current_app, 'game'):
        if Game.query.count() == 0:
            game_start()
        else:
            current_app.game = Game.query.order_by(desc(Game.id)).first()
            current_app.round = GameRound.query.filter_by(
                game_id=current_app.game.id).order_by(desc(GameRound.number)).first()
    emit('connect_message', {'message': 'Connected', 'current_game_content':
        json.dumps(current_app.game.info()), "current_round": json.dumps(current_app.round.info()),
                             'current_user': current_user.info() if current_user.is_authenticated else None})


@socket_io.on('disconnect')
def disconnect():
    if current_user.is_authenticated:
        current_app.users.remove(current_user.id)


def game_start():
    content, origin, author = api.get_poem()
    game = Game()
    game.text = content
    game.title = origin
    game.author = author
    db.session.add(game)
    db.session.commit()
    current_app.game = game
    round = GameRound()
    round.text = game.cleared_text()[0]
    round.number = 0
    round.real_number = 0
    round.game = game
    db.session.add(round)
    db.session.commit()
    current_app.round = round
    emit("game_start", {'message': "新游戏开始",
                        'data': json.dumps(game.info())}, broadcast=True)


def round_start():
    game = current_app.game
    round = current_app.round
    if round.number == len(game.cleared_text()) - 1:
        emit("game_end", {'message': "游戏结束"}, broadcast=True)
        game_start()
        return
    else:
        roundnew = GameRound()
        roundnew.text = game.cleared_text()[round.number + 1]
        roundnew.number = round.number + 1
        if game.text[round.real_number + 1] in ['，', '？', '。', '！', '。', '：']:
            roundnew.real_number = round.real_number + 2
        else:
            roundnew.real_number = round.real_number + 1
        roundnew.game = game
        db.session.add(roundnew)
        db.session.commit()
        current_app.round = roundnew
        emit("round_start", {'message': "新回合开始", 'data': json.dumps(
            roundnew.info())}, broadcast=True)


@socket_io.on('answer')
# @login_required
def answer(data):
    if not current_user.is_authenticated:
        emit("answer_check", {'message': "请先登录"})
        return
    text = data['data']
    r = Record()
    if len(api.clear_mark(text)) <= 8 or len(api.clear_mark(text)) >= 30:
        emit('answer_check', {'message': '长度不符合要求'})
        return
    w = text.find("（）")
    if w == -1:
        emit('answer_check', {'message': '没有找到括号'})
        return
    char = current_app.round.get_character()
    text = text[:w] + char + text[w + 2:]
    if api.clear_mark(current_app.game.text).find(api.clear_mark(text)) != -1 or api.clear_mark(text).find(
            api.clear_mark(current_app.game.text)) != -1:
        emit('answer_check', {'message': '发原诗，卡 bug？'})
        return
    if text[len(text) - 1] != '。' and text[len(text) - 1] != '？' and text[len(text) - 1] != '！' and text[
        len(text) - 1] != '；':
        emit('answer_check', {'message': '末尾需要有标点符号'})
        return
    try:
        check = api.search_poem(text)
    except Exception as e:
        print(e)
        emit("answer_check", {'message': '出错了，大概率找不到这句诗'})
        return
    if check:
        if not check.is_valid():
            emit('answer_check', {'message': check.error_msg()})
            return
        r.line = check.content
        r.title = check.title
        r.author = check.author
        r.user = current_user
        r.game = current_app.game
        r.gameround = current_app.round
        current_user.coin = current_user.get_coin() + 1
        db.session.add(r)
        db.session.commit()
        # round_start()
        emit('answer_check', {'message': '提交成功', 'data': json.dumps({
            'title': r.title, 'author': r.author})})
        emit('record_add', {'message': '已有人答出',
                            'data': json.dumps(r.info())}, broadcast=True)
        round_start()
    else:
        emit('answer_check', {'message': '没有找到这句诗'})


@socket_io.on('test')
def test():
    emit('test', {'game': json.dumps(current_app.game.info()),
                  'round': json.dumps(current_app.round.info())})


@socket_io.on('skip')
@login_required
def skip():
    if current_user.admin:
        emit('skip_check', {'status': 'success', 'message': '管理员跳过'})
        round_start()
    elif current_user.get_coin() >= 50:
        current_user.coin -= 50
        db.session.commit()
        emit('skip_check', {'status': 'success', 'message': '花费 50 金币，剩余 {}'.format(current_user.get_coin())})
        round_start()
    else:
        emit('skip_check', {'status': 'error', 'message': '金币不足，剩余 {}'.format(current_user.get_coin())})


@socket_io.on('talk_message')
def talk_message(data):
    socket_io.emit('talk', {'message': data, 'user': json.dumps(current_user.info())})
