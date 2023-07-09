from sqlalchemy import desc, func
import json
import random
from flask_socketio import SocketIO, emit
from flask_moment import Moment
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, current_app
import time
import os
from sys import platform
from dotenv import load_dotenv
from os import environ, path

DEV = platform == 'win32'

load_dotenv(path.join(path.abspath(path.dirname(__file__)), '.env'))
app = Flask(__name__)
app.secret_key = environ.get('sk')
moment = Moment(app)

from models import *

DIALECT = 'mysql'
DRIVER = 'pymysql'
USERNAME = 'poem_snake'
PASSWORD = environ.get('mysqlpassword')
HOST = '127.0.0.1'
PORT = '3306'
DATABASE = 'poem_snake'
app.config['SQLALCHEMY_DATABASE_URI'] = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
    DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE)
if DEV:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.root_path + '/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

from announcement import announcement
from account import account, login_manager
from gameapi import gameapi
from game import socket_io

app.register_blueprint(announcement)
app.register_blueprint(account)
app.register_blueprint(gameapi)
login_manager.init_app(app)
login_manager.login_view = 'account.login'
socket_io.init_app(app)

with app.app_context():
    current_app.users = []

@app.route('/')
def main():
    v = random.random()
    return render_template('index.html', v=v)


if __name__ == '__main__':
    if DEV:
        socket_io.run(app)
    else:
        socket_io.run(app, host='0.0.0.0', port=19999)
