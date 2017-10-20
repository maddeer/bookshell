#!/usr/bin/env python3

import re
from datetime import datetime

from flask import Flask, abort, request, render_template, session, make_response
from flask import redirect, url_for

from model.models import User, Book, Chapter, make_hash, db_session
from export.exporttopdf import make_pdf_book

app = Flask(__name__)

@app.route('/')
def index():
    #username = request.cookies.get('username')
    book = Book()
    offset = request.args.get('next')
    if not offset:
        offset = 0
    book_info = book.query.limit(25).offset(offset).all()
    username = session.get('username')
    return render_template('index.tmpl', username=username, book=book_info)


@app.route('/login', methods=['POST'])
def login():
    user = User()

    login = request.form.get('login')
    password = request.form.get('password')

    user_data = user.query.filter( User.user_name == login ).first()
    if not user_data:
        return render_template('login.tmpl', login='No login')

    if user.check_user_pass(user_id=user_data.id, password=password):
        render = render_template('login.tmpl', login=login)
        #resp = make_response(render)
        #resp.set_cookie('username', user_data.user_name)
        session['username'] = user_data.user_name
        session['user_id'] = user_data.id
        return redirect(url_for('index'))
    else:
        return render_template('login.tmpl', login='No login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/book/<int:book_id>')
def book(book_id):
    book = Book()
    date = datetime.utcnow()
    username = session.get('username')
    user_id = session.get('user_id')

    if not user_id:
        user_id = 0

    book_info = book.get_book_info(book_id=book_id, user_id=user_id, date_now=date)
    if not book_info.get('book_data'):
        abort(404)

    return render_template(
                'book.tmpl',
                username=username,
                book=book_info,
            )


@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    chapter = Chapter()
    date = datetime.utcnow()
    username = session.get('username')
    user_id = session.get('user_id')

    if not user_id:
        user_id = 0

    chapter_info = chapter.get_chapter_info(chapter_id, user_id, date)

    if not chapter_info:
        abort(404)

    return render_template(
                'chapter.tmpl',
                username=username,
                book=chapter_info,
            )


@app.route('/bookpdf/<int:book_id>')
def bookpdf(book_id):
    book = Book()
    username = session.get('username')
    user_id = session.get('user_id')

    if not user_id:
        user_id = 0

    book_info = book.get_book_info(book_id=book_id, user_id=user_id)

    if not book_info:
        abort(404)

    book_file = make_pdf_book(book_info).replace('static/','')
    return app.send_static_file(book_file)


@app.route('/chapterpdf/<int:chapter_id>')
def chapterpdf(chapter_id):
    chapter = Chapter()
    username = session.get('username')
    user_id = session.get('user_id')

    if not user_id:
        user_id = 0

    book_info = chapter.get_chapter_info(chapter_id=chapter_id, user_id=user_id)

    if not book_info:
        abort(404)

    book_file = make_pdf_book(book_info).replace('static/','')
    return app.send_static_file(book_file)

@app.route('/profile/', defaults={'user_id': None}, methods=['POST','GET'],)
@app.route('/profile/<int:user_id>', methods=['POST','GET'])
def profile(user_id=None):
    username = session.get('username')
    session_user_id = session.get('user_id')
    owner=False

    if not user_id:
        user_id = session_user_id

    edit = False

    user = User()
    user_data = user.query.filter( User.id == user_id ).first()

    if session_user_id == user_id:
        edit_raw = request.args.get('edit', 'False')
        if edit_raw.capitalize() == 'True':
            edit = True

        owner=True

        if request.form:
            update_profile(user_data=user_data, update_form=request.form)

    return render_template(
            'user_profile.tmpl',
            username=username,
            user_data=user_data,
            owner=owner,
            edit=edit
            )


def update_profile(user_data=None, update_form=None):
    if user_data == None and update_form == None:
        return None 

    if update_form.get('first_name'):
        user_data.first_name=update_form.get('first_name')
    
    if update_form.get('middle_name'):
        user_data.middle_name=update_form.get('middle_name')

    if update_form.get('last_name'):
        user_data.last_name=update_form.get('last_name')

    if update_form.get('telegram_login'):
        user_data.telegram_login=update_form.get('telegram_login')

    if update_form.get('about'):
        user_data.about=update_form.get('about')

    if update_form.get('email'):
        user_data.email=update_form.get('email')

    db_session.commit()
    return 'OK'


if __name__ == '__main__':                                                                                                      
    app.secret_key = b'o7E\xd7\xf8q\xdc#\xfe\xae\x11\xba\x91n.\x86\xe8.q<@I?\xc2'
    app.run(port=5000, debug=True)

