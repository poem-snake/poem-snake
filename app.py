import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
import api
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from os import environ, path
from dotenv import load_dotenv
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_moment import Moment
from flask_socketio import SocketIO, emit
import datetime
import json

load_dotenv(path.join(path.abspath(path.dirname(__file__)), '.env'))
app = Flask(__name__)
app.secret_key = environ.get('sk')

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'songhongyi'
PASSWORD = environ.get('mysqlpassword')
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'poem_snake'
app.config['SQLALCHEMY_DATABASE_URI'] = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
    DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+app.root_path+'/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socket_io = SocketIO(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Record (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(
        'User', backref=db.backref('Record', lazy='dynamic'))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    game = db.relationship('Game')


class Game (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    record_id = db.Column(db.Integer, db.ForeignKey('record.id'))
    record = db.relationship(
        'Record', backref=db.backref('Game', lazy='dynamic'))

    def info(self):
        return {'text': self.text, 'title': self.title, 'author': self.author}


class GameRound (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # text = db.Column(db.String(5))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship(
        'Game', backref=db.backref('GameRound', lazy='dynamic'))
    number = db.Column(db.Integer)

    def get_character(self):
        return self.game.text[self.number]

    def info(self):
        return {'text': self.get_character(), 'number': self.number}


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    class RegisterForm(FlaskForm):
        username = StringField('Username', validators=[
                               DataRequired(), Length(1, 20)])
        password = PasswordField('Password', validators=[
                                 DataRequired(), Length(1, 128)])
        password_check = PasswordField('Password_check', validators=[
                                       DataRequired(), Length(1, 128), EqualTo("password")])
        submit = SubmitField('Register')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Register successfully.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    class LoginForm(FlaskForm):
        username = StringField('Username', validators=[
                               DataRequired(), Length(1, 20)])
        password = PasswordField('Password', validators=[
                                 DataRequired(), Length(1, 128)])
        submit = SubmitField('Log in')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Username does not exist.')
            return redirect(url_for('login'))
        if not user.check_password(form.password.data):
            flash('Password is wrong.')
            return redirect(url_for('login'))
        login_user(user, True)
        flash('Login successfully.', 'success')
        return redirect(url_for('main'))
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@socket_io.on('connect')
def connect():
    game_start()
    emit('connect_massage', {'message': 'Connected', 'current_game_content':
                             json.dumps(current_app.game.info()), "current_round": json.dumps(current_app.round.info())})


@socket_io.on('disconnect')
def disconnect():
    pass


def clear_mark(string):
    return string.replace("，", "").replace("；", "").replace("。", "").replace("！", "").replace("？", "")


def game_start():
    content, origin, author = api.get_poem()
    game = Game()
    game.text = clear_mark(content)
    game.title = origin
    game.author = author
    db.session.add(game)
    db.session.commit()
    current_app.__add__
    current_app.game = game
    round = GameRound()
    round.text = game.text[0]
    round.number = 0
    round.game = game
    db.session.add(round)
    db.session.commit()
    current_app.round = round
    emit("game_start", {'message': "新游戏开始",
         'data': json.dumps(game.info())}, broadcast=True)


def round_start():
    game = current_app.game
    round = current_app.round
    if round.number == len(game.text) - 1:
        emit("game_end", {'message': "游戏结束"}, broadcast=True)
        return
    else:
        roundnew = GameRound()
        roundnew.text = game.text[round.number+1]
        roundnew.number = round.number+1
        roundnew.game = game
        db.session.add(roundnew)
        db.session.commit()
        current_app.round = roundnew
        emit("round_start", {'message': "新回合开始", 'data': json.dumps(
            roundnew.info())}, broadcast=True)


@socket_io.on('answer')
@login_required
def answer(text):
    r = Record()
    if len(text) <= 7 or len(text) >= 20:
        emit('answer_check', {'message': '长度不符合要求'})
        return
    w = text.find("（）")
    if w == -1:
        emit('answer_check', {'message': '没有找到括号'})
        return
    char = current_app.round.get_character()
    text = text[:w]+char+text[w+2]
    check = api.search_poem(text)
    if check:
        r.line = text
        r.title = check[0]
        r.author = check[1]
        r.user = current_user
        db.session.add(r)
        db.session.commit()
        emit('answer_check', {'message': '提交成功', 'data': json.dumps({
             'title': check[0], 'author': check[1]})})
        emit('record_add', {'message': '已有人答出', 'data': json.dumps({
             'title': check[0], 'author': check[1], 'text': text})}, broadcast=True)


if __name__ == '__main__':
    socket_io.run(app)
