import eventlet
from sqlalchemy import desc, func
eventlet.monkey_patch()
import json
import datetime
import random
from flask_socketio import SocketIO, emit
from flask_moment import Moment
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import environ, path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import api
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import SubmitField, StringField, PasswordField
from flask_wtf import FlaskForm
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
import time
from libgravatar import Gravatar


load_dotenv(path.join(path.abspath(path.dirname(__file__)), '.env'))
app = Flask(__name__)
app.secret_key = environ.get('sk')

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'poem_snake'
PASSWORD = environ.get('mysqlpassword')
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'poem_snake'
app.config['SQLALCHEMY_DATABASE_URI'] = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
    DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+app.root_path+'/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, session_options={"expire_on_commit": False})
migrate = Migrate(app, db)
moment = Moment(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socket_io = SocketIO(app, logger=True, engineio_logger=True, cors_allowed_origins="*")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def info(self):
        return {
            'id': self.id,
            'username': self.username,
            'gravatar': Gravatar(self.email).get_image(default='identicon').replace('www.gravatar.com', 'gravatar.w3tt.com')
        }


class Record (db.Model):
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
            'gravatar': Gravatar(self.user.email).get_image(default='identicon').replace('www.gravatar.com', 'gravatar.w3tt.com'),
            'time': str(self.time),
            'username': self.user.username,
            'round': self.gameround.info(),
        }


class Game (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    records = db.relationship('Record')

    def info(self):
        return {'text': self.text, 'title': self.title, 'author': self.author}

    def cleared_text(self):
        return clear_mark(self.text)


class GameRound (db.Model):
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


users = []


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@app.route('/')
def main():
    v = random.random()
    return render_template('index.html', v=v)


@app.route('/register', methods=['GET', 'POST'])
def register():
    class RegisterForm(FlaskForm):
        username = StringField('Username', validators=[
                               DataRequired(), Length(1, 20)])
        password = PasswordField('Password', validators=[
                                 DataRequired(), Length(1, 128)])
        password_check = PasswordField('Password_check', validators=[
                                       DataRequired(), Length(1, 128), EqualTo("password")])
        email = StringField('Email', validators=[
                            DataRequired(), Length(1, 50)])
        submit = SubmitField('Register')
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.email = form.email.data
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
    if current_user.is_authenticated:
        users.append(current_user.id)
    if not hasattr(current_app, 'game'):
        if Game.query.count() == 0:
            game_start()
        else:
            current_app.game = Game.query.order_by(desc(Game.id)).first()
            current_app.round = GameRound.query.filter_by(
                game_id=current_app.game.id).order_by(desc(GameRound.number)).first()
    emit('connect_message', {'message': 'Connected', 'current_game_content':
                             json.dumps(current_app.game.info()), "current_round": json.dumps(current_app.round.info())})


@socket_io.on('disconnect')
def disconnect():
    if current_user.is_authenticated:
        users.remove(current_user.id)


@app.route('/api/users')
def get_users():
    return jsonify([User.query.filter_by(id=u).first().info() for u in users])


def clear_mark(string):
    return string.replace("???", "").replace("???", "").replace("???", "").replace("???", "").replace("???", "").replace("???", "")


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
    emit("game_start", {'message': "???????????????",
         'data': json.dumps(game.info())}, broadcast=True)


def round_start():
    game = current_app.game
    round = current_app.round
    if round.number == len(game.cleared_text()) - 1:
        time.sleep(5)
        emit("game_end", {'message': "????????????"}, broadcast=True)
        time.sleep(5)
        game_start()
        return
    else:
        roundnew = GameRound()
        roundnew.text = game.cleared_text()[round.number+1]
        roundnew.number = round.number+1
        if game.text[round.real_number+1] == '???' or game.text[round.real_number+1] == '???' or game.text[round.real_number+1] == '???' or game.text[round.real_number+1] == '???' or game.text[round.real_number+1] == '???' or game.text[round.real_number+1] == '???':
            roundnew.real_number = round.real_number+2
        else:
            roundnew.real_number = round.real_number+1
        roundnew.game = game
        db.session.add(roundnew)
        db.session.commit()
        current_app.round = roundnew
        time.sleep(5)
        emit("round_start", {'message': "???????????????", 'data': json.dumps(
            roundnew.info())}, broadcast=True)


@socket_io.on('answer')
# @login_required
def answer(data):
    if not current_user.is_authenticated:
        emit("answer_check", {'message': "????????????"})
        return
    text = data['data']
    r = Record()
    if len(text) <= 10 or len(text) >= 30:
        emit('answer_check', {'message': '?????????????????????'})
        return
    w = text.find("??????")
    if w == -1:
        emit('answer_check', {'message': '??????????????????'})
        return
    char = current_app.round.get_character()
    text = text[:w]+char+text[w+2:]
    if current_app.game.text.find(text) != -1 or text.find(current_app.game.text) != -1:
        emit('answer_check', {'message': '??????????????? bug???'})
        return
    if text[len(text)-1] != '???' and text[len(text)-1] != '???' and text[len(text)-1] != '???' and text[len(text)-1] != '???':
        emit('answer_check', {'message': '???????????????????????????'})
        return
    try:
        check = api.search_poem(text)
    except Exception as e:
        emit("answer_check", {'message': '???????????????????????????????????????'})
        return
    if check:
        r.line = text
        r.title = check[0]
        r.author = check[1]
        r.user = current_user
        r.game = current_app.game
        r.gameround = current_app.round
        db.session.add(r)
        db.session.commit()
        # round_start()
        emit('answer_check', {'message': '????????????', 'data': json.dumps({
             'title': check[0], 'author': check[1]})})
        emit('record_add', {'message': '???????????????',
             'data': json.dumps(r.info())}, broadcast=True)
        round_start()
    else:
        emit('answer_check', {'message': '?????????????????????'})


@socket_io.on('test')
def test():
    emit('test', {'game': json.dumps(current_app.game.info()),
         'round': json.dumps(current_app.round.info())})


@app.route('/api/history')
# @login_required
def history():
    last = request.args.get('last', 19260817, type=int)
    records = Record.query.filter(Record.id < last).order_by(
        desc(Record.id)).limit(10).all()
    return jsonify([r.info() for r in records])


@app.route('/api/ranklist')
def ranklist():
    perpage = request.args.get('perpage', 10, type=int)
    page = request.args.get('page', 1, type=int)
    users = User.query.join(Record, Record.user_id == User.id).with_entities(User.id, User.username, func.count(
        Record.id)).group_by(User.id).order_by(desc(func.count(Record.id))).paginate(page, perpage, False)
    first = (page-1)*perpage+1
    return jsonify({'page': page, "perpage": perpage, 'data': [{"num": first+idx, "uid": u[0], "username":u[1], 'count':u[2]} for idx, u in enumerate(users.items)]})


@socket_io.on('skip')
@login_required
def skip():
    if current_user.admin:
        round_start()

@socket_io.on('talk_message')
def talk_message(data):
    socket_io.emit('talk',{'message':data,'user':json.dumps(current_user.info())})


if __name__ == '__main__':
    socket_io.run(app)
