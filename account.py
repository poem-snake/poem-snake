from flask import render_template, redirect, url_for, flash, Blueprint, jsonify
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
from models import db, User
from PIL import Image
import os

account = Blueprint('account', __name__, url_prefix='/account')

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


@account.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('account.register'))
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Register successfully.', 'success')
        return redirect(url_for('account.login'))
    return render_template('register.html', form=form)


@account.route("/login", methods=['GET', 'POST'])
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
            return redirect(url_for('account.login'))
        if not user.check_password(form.password.data):
            flash('Password is wrong.')
            return redirect(url_for('account.login'))
        login_user(user, True)
        flash('Login successfully.', 'success')
        return redirect(url_for('main'))
    return render_template('login.html', form=form, nake=True)


@account.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@account.route('/crop', methods=['POST'])
def crop_avatar():
    class CropAvatarForm(FlaskForm):
        x1 = HiddenField()
        y1 = HiddenField()
        x2 = HiddenField()
        y2 = HiddenField()
        submit = SubmitField('Crop')

    form = CropAvatarForm(meta={'csrf': False})
    if form.validate_on_submit():
        x1 = int(form.x1.data)
        y1 = int(form.y1.data)
        x2 = int(form.x2.data)
        y2 = int(form.y2.data)
        filename = str(current_user.id) + '.png'
        if not os.path.exists(os.path.join('./static/avatars/', filename)):
            return jsonify({'status': 'error', 'message': '请先上传图片'})
        im = Image.open(os.path.join('./static/avatars/', filename))
        im = im.crop((x1, y1, x2, y2))
        im = im.resize((512, 512), Image.ANTIALIAS)
        im.save(os.path.join('./static/avatars/', filename))
        current_user.avatar_uploaded = True
        db.session.commit()
        return jsonify({'status': 'success', 'message': '上传成功'})
    return jsonify({'status': 'error', 'message': form.errors})


@account.route('/avatar/')
@login_required
def change_avatar():
    file_name = str(current_user.id) + '.png'
    if os.path.exists(os.path.join('./static/avatars/', file_name)) and not current_user.avatar_uploaded:
        t = 'crop'
    else:
        t = 'upload'
    return render_template('avatar.html', type=t)
