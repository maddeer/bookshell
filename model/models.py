#!/usr/bin/env python3

import os
import re

from hashlib import sha384
from binascii import hexlify

from datetime import datetime

from sqlalchemy import create_engine, or_, literal_column, func
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, SmallInteger
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, joinedload
from sqlalchemy.ext.declarative import declarative_base


DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'bookshell.db')

engine = create_engine('sqlite:///'+DATABASE_PATH)

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

def make_hash(passwd, salt=None):
    if not salt:
        salt=hexlify(os.urandom(16)).decode('utf-8')

    pass_salt = salt + passwd
    password_hash = sha384(pass_salt.encode('utf-8')).hexdigest()
    return salt + password_hash


class Role(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50))

    def __init__(self, role_name=None):
        self.role_name = role_name

    def __repr__(self):
        return('<Role {} {}>'.format(self.id, self.role_name))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(25), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), index=True)
    middle_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    telegram_login = Column(String(50), index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    about = Column(String(255))
    role_id = Column(Integer, ForeignKey('user_role.id'))
    telegram_id = Column(Integer)

    __table_args__ = (
            Index(
            'ix_user_fullname',
            first_name,
            middle_name,
            last_name,
            ),)

    def __init__(
                self,
                user_name=None,
                password=None,
                first_name=None,
                middle_name=None,
                last_name=None,
                telegram_login=None,
                email=None,
                role=None,
                about=None,
                telegram_id=None,
                ):

        self.user_name = user_name
        self.password = password
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.telegram_login = telegram_login
        self.email = email
        self.about = about
        self.role = role
        self.telegram_id = telegram_id

    def __repr__(self):
        return('<User {} {}>'.format(self.user_name, self.full_name))

    def check_user_pass(self, user_id, password=None):
        user_info = self.query.filter( User.id == user_id ).first()

        salt = user_info.password[0:32]
        salt_hash = make_hash(password, salt)

        if user_info.password == salt_hash:
            return True
        else:
            return False

    @property
    def full_name(self):
        if not self.first_name:
            self.first_name = ''
        if not self.middle_name:
            self.middle_name = ''
        if not self.last_name:
            self.last_name = ''

        return ' '.join([
                        self.first_name,
                        self.middle_name,
                        self.last_name
                        ]).strip().replace('  ',' ')

    @staticmethod
    def get_id_by_telegram_name(name):
        user = User.query.filter(User.telegram_login == name).first()
        if user is not None:
            return user.id
        else:
            return 0


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    genre_name = Column(String(25), nullable=False)
    genre_name_type = Column(String(25))
    parent = Column(Integer, ForeignKey('genre.id')) 
    genre = relationship('GenreBook', backref='genre')


    def __init__(self, genre_name=None, genre_name_type=None, parent=None):
        self.genre_name = genre_name
        self.genre_name_type = genre_name_type
        self.parent = parent

    def __repr__(self):
        return('<Genre {} {}>'.format(self.id, self.genre_name))

    @staticmethod
    def get_all():
        return Genre.query.filter( Genre.genre_name_type != '' ).order_by( Genre.id ).all()

    @staticmethod
    def get_parents():
        return Genre.query.filter( Genre.genre_name_type == '' ).order_by( Genre.id ).all()

    @staticmethod
    def get_children(parent_id):
        return Genre.query.filter( Genre.parent == parent_id ).order_by( Genre.id ).all()

    @staticmethod
    def get_all_counted():
        genre = Genre()
        return genre.query.add_column(
                    func.count(
                        GenreBook.book_id
                    )).outerjoin(
                        GenreBook,
                        GenreBook.genre_id == Genre.id,
                    ).filter(
                        Genre.genre_name_type != ''
                    ).group_by(Genre.id).all()


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    book_name = Column(String(255), nullable=False)
    book_description = Column(Text)
    genre = relationship('GenreBook', backref='book')
    chapters = relationship('Chapter', backref='book')
    authors = relationship('Author', backref='books_author')

    def __init__(self, book_name=None, book_description=None):
        self.book_name = book_name
        self.book_description = book_description

    def __repr__(self):
        return('<Book {} {}>'.format(self.id, self.book_name))

    @staticmethod
    def get_book(book_id):
        book_chapters = Chapter.query.filter(
            Chapter.book_id == book_id,
        ).order_by(
            Chapter.chapter_number,
        ).all()

        return book_chapters

    def get_book_info(self, book_id, user_id, date_now=datetime.utcnow()):
        book_info = self.query.filter(Book.id == book_id).first()

        authors = User.query.join(
            Author,
            Author.user_id == User.id,
        ).filter(
            Author.book_id == book_id,
        ).all()

        if user_id in [author.id for author in authors]:

            book_chapters = Chapter.query.add_column(
                literal_column("'allow'").label('access')
            ).filter(
                Chapter.book_id == book_id,
            ).filter(
                or_( Chapter.deleted < 2, Chapter.deleted == None )
            ).order_by(
                Chapter.chapter_number,
            ).all()

        else:
            allowed = Chapter.query.add_column(
                literal_column("'allow'").label('access')
            ).outerjoin(
                Grant,
                Grant.allowed_chapter == Chapter.id
            ).filter(
                or_(
                    Grant.user_id == 2,
                    Chapter.date_to_open < datetime.utcnow()
                    )
            ).filter(
                Chapter.book_id == book_id,
            ).filter(
                or_(Chapter.deleted < 1, Chapter.deleted == None )
            )

            not_in = db_session.query(
                Chapter.id
            ).outerjoin(
                Grant,
                Grant.allowed_chapter == Chapter.id
            ).filter(
                Chapter.book_id == book_id,
            ).filter(
                or_(
                    Grant.user_id == user_id,
                    Chapter.date_to_open < datetime.utcnow()
            ))

            denied = Chapter.query.add_column(
                literal_column("'deny'").label('access')
            ).filter(
                ~Chapter.id.in_(not_in)
            ).filter(
                Chapter.book_id == book_id,
            )

            book_chapters = allowed.union(
                denied
            ).order_by(
                Chapter.chapter_number
            ).all()

        book_dict = {
            'book_data': book_info,
            'book_authors': authors,
            'book_chapters': book_chapters,
            }
        return book_dict

    def get_books_by_genre(self,genre_id):
        genre = Genre()
        parent_genres = genre.get_parents()

        if genre_id in [ genre_row.id for genre_row in parent_genres ]:
            children = genre.get_children(genre_id)
            return self.query.outerjoin( 
                        GenreBook,
                        GenreBook.book_id == Book.id 
                    ).filter(
                        GenreBook.genre_id.in_(
                            [child.id for child in children]
                    )).options(
                        joinedload(
                            Book.authors
                        ).joinedload(
                            Author.user
                    )).all()
        else:
            return self.query.outerjoin( 
                        GenreBook,
                        GenreBook.book_id == Book.id
                    ).filter(
                        GenreBook.genre_id == genre_id
                    ).options(
                        joinedload(
                            Book.authors
                        ).joinedload(
                            Author.user
                    )).all()

class GenreBook(Base):
    __tablename__ = 'genre_book'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'))
    genre_id = Column(Integer, ForeignKey('genre.id'))

    def __init__(self, book_id=None, genre_id=None):
        self.book_id = book_id
        self.genre_id = genre_id

    def __repr__(self):
        return('<GenreBook {} {}>'.format(self.book_id, self.genre_id))


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    book_id = Column(Integer, ForeignKey('book.id'))
    user = relationship('User', uselist=False, lazy='joined', backref='books_author')

    def __init__(self, user_id=None, book_id=None):
        self.user_id = user_id
        self.book_id = book_id

    def __repr__(self):
        return('<Author {} {}>'.format(self.user_id, self.book_id))

    @staticmethod
    def get_authors_with_books():
        user_list = []
        user_with_books = Author.query.group_by(Author.user_id).all()
        for line in user_with_books:
            user_list.append(line.user_id)
        return user_list



class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(String(255))
    date_to_open = Column(DateTime, default=datetime.utcnow)
    last_edited = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(SmallInteger)
    chapter_text = Column(Text)

    alowed_user = relationship('Grant', backref='alowed')

    def __init__(
                self,
                book_id=None,
                chapter_number=None,
                chapter_title=None,
                date_to_open=None,
                chapter_text=None,
                deleted=0,
                ):

        self.book_id = book_id
        self.chapter_number = chapter_number
        self.chapter_title = chapter_title
        self.date_to_open = date_to_open
        self.chapter_text = chapter_text
        self.deleted = deleted

    def __repr__(self):
        return('<Chapter {} {} {}>'.format(
                                            self.id,
                                            self.chapter_title,
                                            self.book_id
                                            ))

    def get_chapter_info(self, chapter_id, user_id, date_now=datetime.utcnow()):
        chapter_info = self.query.filter(Chapter.id == chapter_id).first()
        if not chapter_info:
            return None

        book_info = Book.query.filter(Book.id == chapter_info.book_id).first()

        authors = User.query.join(
            Author,
            Author.user_id == User.id,
        ).filter(
            Author.book_id == book_info.id,
        ).all()

        if user_id in [author.id for author in authors]:

            book_chapters = self.query.add_column(
                literal_column("'allow'").label('access')
            ).filter(
                Chapter.id == chapter_id,
            ).filter(
                or_( Chapter.deleted < 2, Chapter.deleted == None )
            ).all()

        else:
            allowed = self.query.add_column(
                literal_column("'allow'").label('access')
            ).outerjoin(
                Grant,
                Grant.allowed_chapter == Chapter.id
            ).filter(
                or_(
                    Grant.user_id == user_id,
                    Chapter.date_to_open < datetime.utcnow()
                    )
            ).filter(
                Chapter.id == chapter_id,
            ).filter(
                or_(Chapter.deleted < 1, Chapter.deleted == None )
            )

            not_in = db_session.query(
                Chapter.id
            ).outerjoin(
                Grant,
                Grant.allowed_chapter == Chapter.id
            ).filter(
                Chapter.id == chapter_id,
            ).filter(
                or_(
                    Grant.user_id == user_id,
                    Chapter.date_to_open < datetime.utcnow()
            ))

            denied = Chapter.query.add_column(
                literal_column("'deny'").label('access')
            ).filter(
                Chapter.id == chapter_id,
            ).filter(
                ~Chapter.id.in_(not_in)
            )

            book_chapters = allowed.union(
                denied
            ).order_by(
                Chapter.chapter_number
            ).all()

        book_dict = {
            'book_data': book_info,
            'book_authors': authors,
            'book_chapters': book_chapters,
            }
        return book_dict

    @property
    def short_text(self):
        return self.chapter_text[:300] + '...'

    @property
    def chapter_text_br(self):
        return re.sub(r"(.*)", r"<p>\1</p>", self.chapter_text)


class Grant(Base):
    __tablename__ = 'chapter_grant_allowed'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    allowed_chapter = Column(Integer, ForeignKey('chapter.chapter_number'))

    def __init__(self, user_id=None, allowed_chapter=None):
        self.user_id = user_id
        self.allowed_chapter = allowed_chapter

    def __repr__(self):
        return('<Grant {} {}>'.format(self.user_id, self.allowed_chapter))


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
