#!/usr/bin/env python3

from flask import Flask, abort, request, render_template, session, make_response
from flask import redirect, url_for
#from flask.ext.session import Session

from model.models import User, Book

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
        return redirect(url_for('index'))
    else:
        return render_template('login.tmpl', login='No login')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/book:int book_id')
def book():
    pass

if __name__ == '__main__':                                                                                                       
    app.secret_key = b'o7E\xd7\xf8q\xdc#\xfe\xae\x11\xba\x91n.\x86\xe8.q<@I?\xc2'
    app.run(port=5000, debug=True)

