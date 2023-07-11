from flask import render_template, redirect, url_for, flash, Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo
from models import db, User
from PIL import Image
from auth import check_paste
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


@account.route('/luogu', methods=['GET', 'POST'])
@login_required
def luogu():
    via = request.args.get('api', type=bool, default=False)
    if via:
        if request.method != 'POST':
            return jsonify({'status': 'error', 'message': '请使用POST方法'})
        luogu_id = request.form.get('luogu_id')
        paste = request.form.get('paste')
        check = check_paste(luogu_id, paste)
        if check[0]:
            user = User.query.filter_by(luogu_id=luogu_id).first()
            if user:
                return jsonify({'status': 'error', 'message': '该洛谷账号已被绑定'})
            current_user.luogu_id = luogu_id
            current_user.coin = current_user.get_coin() + 100
            db.session.commit()
            return jsonify({'status': 'success', 'message': '绑定成功'})
        else:
            return jsonify({'status': 'error', 'message': check[1]})

    class LuoguForm(FlaskForm):
        luogu_id = StringField('Luogu ID', validators=[DataRequired(), Length(1, 10)])
        paste = StringField('Paste', validators=[DataRequired(), Length(1, 10)])
        submit = SubmitField('Submit')

    form = LuoguForm()
    if form.validate_on_submit():
        check = check_paste(form.luogu_id.data, form.paste.data)
        if check[0]:
            user = User.query.filter_by(luogu_id=form.luogu_id.data).first()
            if user:
                flash('该洛谷账号已被绑定', 'danger')
                return redirect(url_for('account.luogu'))
            current_user.luogu_id = form.luogu_id.data
            current_user.coin = current_user.get_coin() + 100
            db.session.commit()
            flash('绑定成功', 'success')
            return redirect(url_for('main'))
        else:
            flash(f'绑定失败：{check[1]}', 'danger')
            return redirect(url_for('account.luogu'))
    return render_template('luogu.html', form=form)
