#!/usr/bin/env python3

from datetime import datetime

from sqlalchemy import create_engine, or_
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('sqlite:///bookshell.db')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()


class Role(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50))

    def __init__(self, role_name=None):
        self.role_name = role_name

    def __repr__(self):
        return('Role {} {}>'.format(self.id, self.role_name))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(25), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(50), index=True)
    telegram_login = Column(String(50), index=True)
    role_id = Column(Integer, ForeignKey('user_role.id'))

    def __init__(
                self,
                user_name=None,
                password=None,
                full_name=None,
                telegram_login=None,
                role=None
                ):

        self.user_name = user_name
        self.password = password
        self.full_name = full_name
        self.telegram_login = telegram_login
        self.role = role

    def __repr__(self):
        return('<User {} {}>'.format(self.user_name, self.full_name))


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    genre_name = Column(String(25), nullable=False)

    def __init__(self, genre_name=None):
        self.genre_name = genre_name

    def __repr__(self):
        return('<Genre {} {}>'.format(self.id, self.genre_name))


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    book_name = Column(String(255), nullable=False)
    book_description = Column(Text)

    def __init__(self, book_name=None, book_description=None):
        self.book_name = book_name
        self.book_description = book_description

    def __repr__(self):
        return('<Book {} {}>'.format(self.id, self.book_name))

    def get_book_info(self, book_id, user_id):
        date_now = datetime.utcnow()
        book_info = self.query.filter(Book.id == book_id).first()

        authors = User.query.join(
            Author,
            Author.user_id == User.id,
        ).filter(
            Author.book_id == book_id,
        ).all()

        if user_id in [author.id for author in authors]:

            book_chapters = Chapter.query.filter(
                Chapter.book_id == book_id,
            ).filter(
                Chapter.date_to_open < date_now,
            ).order_by(
                Chapter.chapter_number,
            ).all()

        else:
            book_chapters = Chapter.query.outerjoin(
                Grant,
                Grant.allowed_chapter == Chapter.chapter_number,
            ).filter(
                Chapter.book_id == book_id,
            ).filter(
                or_(
                    Chapter.date_to_open < date_now,
                    Grant.user_id == user_id,
                )
            ).group_by(
                Chapter.id,
            ).order_by(
                Chapter.chapter_number,
            ).all()

        book_dict = {
            'book_data': book_info,
            'book_authors': authors,
            'book_chapters': book_chapters,
            }
        return book_dict


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

    def __init__(self, user_id=None, book_id=None):
        self.user_id = user_id
        self.book_id = book_id

    def __repr__(self):
        return('<Author {} {}>'.format(self.user_id, self.book_id))


class Chapter(Base):
    __tablename__ = 'chapter'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_title = Column(String(255))
    date_to_open = Column(DateTime)
    chapter_text = Column(Text)

    def __init__(
                self,
                book_id=None,
                chapter_number=None,
                chapter_title=None,
                date_to_open=None,
                chapter_text=None
                ):

        self.book_id = book_id
        self.chapter_number = chapter_number
        self.chapter_title = chapter_title
        self.date_to_open = date_to_open
        self.chapter_text = chapter_text

    def __repr__(self):
        return('<Chapter {} {} {}>'.format(
                                            self.id,
                                            self.chapter_title,
                                            self.book_id
                                            ))


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
