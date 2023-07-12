from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from libgravatar import Gravatar
import datetime
import api
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"expire_on_commit": False})


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120))
    admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(50), unique=True)
    coin = db.Column(db.Integer)
    avatar_uploaded = db.Column(db.Boolean, default=False)
    luogu_id = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_avatar(self):
        if self.avatar_uploaded:
            return url_for('static', filename='avatars/{}.png'.format(self.id))
        elif self.luogu_id:
            return f'https://cdn.luogu.com.cn/upload/usericon/{self.luogu_id}.png'
        else:
            return api.gravatar(self.email)

    def info(self):
        return {
            'id': self.id,
            'username': self.username,
            'gravatar': self.get_avatar()
        }

    def get_coin(self):
        if self.coin is None:
            self.coin = Record.query.filter_by(user_id=self.id).count()
            db.session.commit()
        return self.coin


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('Record', lazy='dynamic'))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship(
        'Game', backref=db.backref('Record', lazy='dynamic'))
    gameround_id = db.Column(db.Integer, db.ForeignKey('game_round.id'))
    gameround = db.relationship(
        'GameRound', backref=db.backref('Record', lazy='dynamic'))

    def info(self):
        return {
            'id': self.id,
            'line': self.line,
            'title': self.title,
            'author': self.author,
            'gravatar': self.user.get_avatar(),
            'time': str(self.time),
            'username': self.user.username,
            'round': self.gameround.info(),
        }


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    records = db.relationship('Record')

    def info(self):
        return {'text': self.text, 'title': self.title, 'author': self.author}

    def cleared_text(self):
        return api.clear_mark(self.text)


class GameRound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # text = db.Column(db.String(5))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship(
        'Game', backref=db.backref('GameRound', lazy='dynamic'))
    number = db.Column(db.Integer)
    real_number = db.Column(db.Integer)

    def get_character(self):
        return self.game.cleared_text()[self.number]

    def info(self):
        return {'text': self.get_character(), 'number': self.number, 'real_number': self.real_number}


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(1000))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    pinned = db.Column(db.Boolean, default=False)

    def info(self):
        return {'title': self.title, 'content': self.content, 'time': str(self.time), 'pinned': self.pinned}
