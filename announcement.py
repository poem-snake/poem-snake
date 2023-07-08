from flask import Blueprint, render_template, redirect, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
import markdown

from models import db, Announcement

announcement = Blueprint('announcement', __name__)


@announcement.route('/api/announcements')
def get_announcements():
    announcements = Announcement.query.order_by(Announcement.pinned.desc(), Announcement.time.desc()).all()
    return {'announcements': [announcement.info() for announcement in announcements]}


@announcement.route('/api/announcement/newest')
def get_newest_announcement():
    announcement = Announcement.query.order_by(Announcement.time.desc()).first()
    return {'time': int(round(announcement.time.timestamp()))} if announcement else {'time': '0'}


@announcement.route('/announcement/new', methods=['GET', 'POST'])
@login_required
def new_announcement():
    if not current_user.id == 1:
        flash('Permission denied.', 'danger')
        return redirect('/')

    class AnnouncementForm(FlaskForm):
        title = StringField('Title')
        content = TextAreaField('Content')
        pinned = BooleanField('Pinned')
        submit = SubmitField('Submit')

    form = AnnouncementForm()
    if form.validate_on_submit():
        print(form.title.data, form.pinned.data)
        content = markdown.markdown(form.content.data)
        announcement = Announcement(title=form.title.data, content=content, pinned=form.pinned.data)
        db.session.add(announcement)
        db.session.commit()
        flash('Your announcement has been created!', 'success')
        return redirect('/')

    return render_template('new_announcement.html', title='New Announcement', form=form)
