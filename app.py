from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
import datetime

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
    text = db.Column(db.String(100), default='苟利国家生死以岂因祸福避趋之')
    record_id = db.Column(db.Integer, db.ForeignKey('record.id'))
    record = db.relationship(
        'Record', backref=db.backref('Game', lazy='dynamic'))


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
