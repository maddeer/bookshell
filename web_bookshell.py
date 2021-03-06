#!/usr/bin/env python3

import os
from io import BytesIO
from datetime import datetime
from functools import wraps

from flask import Flask, abort, request, render_template, session, make_response
from flask import redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename

from configparser import ConfigParser

from model.models import User, Book, Chapter, Genre, make_hash, db_session
from export.exporttopdf import make_pdf_book
from modules_bookshell import docx_to_text, save_the_book, add_chapter
from export.exporttofb2 import make_fb2_book

UPLOAD_FOLDER = 'books/'
ALLOWED_EXTENSIONS = set(['txt', 'docx'])

app = Flask(__name__)
config = ConfigParser()
config.sections()
config.read('conf/bookshell.conf')
app.secret_key = config['DEFAULT']['WEB_SESSION_KEY']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/')
def index():
    #username = request.cookies.get('username')
    book = Book()
    offset = request.args.get('next')
    if not offset:
        offset = 0
    book_info = book.query.order_by(Book.id.desc()).limit(25).offset(offset).all()
    username = session.get('username')
    genre = Genre()
    counted_genres = genre.get_all_counted()

    return render_template(
                'index.tmpl',
                username=username,
                book=book_info,
                genres=counted_genres,
                nav_get_parents=nav_get_parents(),
            )


@app.route('/login', methods=['POST'])
def login():
    user = User()

    login = request.form.get('login')
    password = request.form.get('password')

    user_data = user.query.filter( User.user_name == login ).first()
    if not user_data:
        return render_template(
                    'login.tmpl',
                    login='No login',
                    nav_get_parents=nav_get_parents(),
                )

    if user.check_user_pass(user_id=user_data.id, password=password):
        render = render_template('login.tmpl', login=login, nav_get_parents=nav_get_parents(),)
        #resp = make_response(render)
        #resp.set_cookie('username', user_data.user_name)
        session['username'] = user_data.user_name
        session['user_id'] = user_data.id
        return redirect(request.referrer) or redirect(url_for('index'))
    else:
        return render_template(
                    'login.tmpl',
                    login='No login',
                    nav_get_parents=nav_get_parents(),
                )


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/book/<int:book_id>')
def book(book_id):
    book = Book()
    username = session.get('username')
    user_id = session.get('user_id')
    owner = False

    if not user_id:
        user_id = 0

    book_info = book.get_book_info(book_id=book_id, user_id=user_id)
    if not book_info.get('book_data'):
        abort(404)

    for author in book_info['book_authors']:
        if author.id == user_id:
            owner = True

    return render_template(
                'book.tmpl',
                username=username,
                book=book_info,
                owner=owner,
                nav_get_parents=nav_get_parents(),
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

    if not chapter_info or not chapter_info['book_chapters']:
        abort(404)

    return render_template(
                'chapter.tmpl',
                username=username,
                book=chapter_info,
                nav_get_parents=nav_get_parents(),
            )


def export_book_method(get_book_info):
    @wraps(get_book_info)
    def make_my_book(id, user_id=0, book_format='pdf'):
        username = session.get('username')
        user_id = session.get('user_id')
        avaliable_formats = ['pdf', 'fb2',]
        
        if book_format not in avaliable_formats:
            abor(404)

        if not user_id:
            user_id = 0

        book_info = get_book_info(id=id, user_id=user_id)

        if not book_info:
            abort(404)

        if book_format == 'pdf': 
            book_file = make_pdf_book(book_info)
        elif book_format == 'fb2': 
            book_file = make_fb2_book(book_info)

        return send_file(
                        BytesIO(book_file['file']), 
                        as_attachment=True,
                        attachment_filename=book_file['file_name'],
                        mimetype=book_file['mimetype'],
                        )
    return make_my_book


@app.route('/exportbook/<string:book_format>/<int:id>')
@export_book_method
def export_book(id, user_id=0):
    book = Book()
    return book.get_book_info(book_id=id, user_id=user_id)


@app.route('/exportchapter/<string:book_format>/<int:id>')
@export_book_method
def export_chapter(id, user_id=0):
    chapter = Chapter()
    return chapter.get_chapter_info(chapter_id=id, user_id=user_id)


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
                edit=edit,
                nav_get_parents=nav_get_parents(),
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


@app.route('/addbook', methods=['POST', 'GET'])
#@login_required
def addbook():
#    if request.method == 'POST':
#        form = AddBookForm(request.form, request.files)
#        errors = form.get_arrors()
#        if errors:
#            for error in errors:
#                flash(error)
#                redirect(url_for('add_book'))
#        else:
#            Book.create(form.data)
#    elif request.method == 'GET':
#        context = {}
#        return render_template(...)
#
#class AddBookFormView(View):
#    def post(self):
#        form = AddBookForm(request.form, request.files)
#        errors = form.get_arrors()
#        if errors:
#            for error in errors:
#                flash(error)
#            redirect(url_for('add_book'))
#        else:
#            Book.create(form.data)
#
#    def get(self):
#        context = {}
#        return render_template()
#
#
######################################
    username = session.get('username')
    user_id = session.get('user_id')

    if not username:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'chapter' not in request.files:
            flash('Вы не вложили файл с первой частью')
            return redirect(url_for('addbook'))
        chapter_file = request.files['chapter']
        if chapter_file.filename == '':
            flash('Вы не вложили файл с первой частью')
            return redirect(url_for('addbook'))

        if not request.form.get('book_name'):
            flash('Нет названия книги')
            return redirect(url_for('addbook'))

        if not request.form.getlist('genres', None):
            flash('Вы не указали ни одного жанра')
            return redirect(url_for('addbook'))

        if chapter_file and allowed_file(chapter_file.filename):
            filename = secure_filename(chapter_file.filename)
            save_book = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            chapter_file.save(save_book)
            book_text = docx_to_text(save_book)
            time_to_open = request.form.get('date')
            book_id = save_the_book(
                        book_name=request.form.get('book_name'),
                        text=book_text,
                        user_id=user_id,
                        description=request.form.get('description', None),
                        chapter_title=request.form.get('chapter_title', None),
                        genre=request.form.getlist('genres'),
                        time_open=datetime.strptime(time_to_open, '%d/%m/%Y'),
                    )
            return redirect(url_for('book', book_id=book_id))

    genre = Genre()
    genre_list = genre.get_all()
    return render_template(
                'add_book.tmpl',
                username=username,
                genre_list=genre_list,
                nav_get_parents=nav_get_parents(),
            )


@app.route('/addchapter/<int:book_id>', methods=['POST', 'GET'])
def add_chapter_web(book_id):
    username = session.get('username')
    user_id = session.get('user_id')
    book = Book()

    if not username:
        return redirect(url_for('index'))

    book_info = book.get_book_info(book_id=book_id, user_id=user_id)
    owner = False

    if not book_info:
        abort(404)

    for author in book_info['book_authors']:
        if author.id == user_id:
            owner = True

    if not owner:
        abort(403)

    if request.method == 'POST':
        if 'chapter' not in request.files:
            flash('Вы не вложили файл с новой частью')
            return redirect(url_for('add_chapter_web', book_id=book_id))
        chapter_file = request.files['chapter']
        if chapter_file.filename == '':
            flash('Вы не вложили файл с новой частью книги')
            return redirect(url_for('add_chapter_web', book_id=book_id))

        if chapter_file and allowed_file(chapter_file.filename):
            filename = secure_filename(chapter_file.filename)
            save_book = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            chapter_file.save(save_book)
            book_text = docx_to_text(save_book)
            time_to_open = request.form.get('date')
            chapter_id = add_chapter(
                                book_id=book_id,
                                user_id=user_id,
                                chapter_title=request.form.get('chapter_title'),
                                time_open=datetime.strptime(request.form.get('date'), '%d/%m/%Y'),
                                text=book_text,
                                chapter_number=request.form.get('chapter_number', None),
                            )
            return redirect(url_for('chapter', chapter_id=chapter_id))

    next_chapter = book_info['book_chapters'][-1][0].chapter_number + 1

    return render_template(
                'add_chapter.tmpl',
                username=username,
                book=book_info,
                next_chapter=next_chapter,
                nav_get_parents=nav_get_parents(),
            )


def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/delete-chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    username = session.get('username')
    user_id = session.get('user_id')

    if not username:
        return redirect(url_for('index'))

    chapter = Chapter()
    book_info = chapter.get_chapter_info(chapter_id=chapter_id, user_id=user_id)
    owner = False

    if not book_info:
        abort(404)

    for author in book_info['book_authors']:
        if author.id == user_id:
            owner = True

    if not owner:
        abort(403)

    if not book_info['book_chapters'][0][0].deleted or book_info['book_chapters'][0][0].deleted == 0: 
        book_info['book_chapters'][0][0].deleted = 1
        db_session.commit()
        return jsonify(deleted=1)
    elif book_info['book_chapters'][0][0].deleted == 1:
        book_info['book_chapters'][0][0].deleted = 0
        db_session.commit()
        return jsonify(deleted=0)
    elif book_info['book_chapters'][0][0].deleted > 1: 
        return jsonify(deleted=1)
    else:
        return jsonify(deleted=0)


@app.route('/genres/<int:genre_id>')
def get_books_by_genre_web(genre_id=110):
    username = session.get('username')
    user_id = session.get('user_id')

    book = Book()
    books = book.get_books_by_genre(genre_id)
    if not books:
        abort(404)

    genre = Genre()
    counted_genres = genre.get_all_counted()
    current_genre = genre.query.filter(Genre.id == genre_id).first()

    return render_template(
                'genre_search.tmpl',
                book=books,
                username=username,
                current_genre=current_genre,
                genres=counted_genres,
                nav_get_parents=nav_get_parents(),
            )

def nav_get_parents():
    genre = Genre()
    return genre.get_parents()


if __name__ == '__main__':
    app.run(port=5000, debug=True)

