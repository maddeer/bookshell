#!/usr/bin/env python3 

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base 

engine = create_engine('sqlite:///bookshell.db') 

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

class Role(Base):
    __tablename__ = 'user_role'
    role_id = Column(Integer, primary_key=True) 
    role_name = Column(String(50))

    def __init__ (self, role_id=None, role_name=None): 
        self.role_id = role_id 
        self.role_name = role_name 

    def __repr__ (self):
        return('Role {} {}>'.format(self.role_id, self.role_name))


class Users(Base):
    __tablename__ = 'users' 
    user_id = Column(Integer, primary_key=True) 
    user_name = Column(String(25), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False) 
    full_name = Column(String(50), index=True)
    telegram_login = Column(String(50), unique=True, index=True)
    role = Column(Integer, ForeignKey('user_role.role_id'))
    
    def __init__ (self, user_name=None, password=None, full_name=None, telegram_login=None, role=None): 
        self.user_name = user_name 
        self.password = password 
        self.full_name = full_name
        self.telegram_login = telegram_login
        self.role = role

    def __repr__ (self):
        return('<Users {} {}>'.format(self.user_name, self.full_name))


class Genre(Base):
    __tablename__ = 'genre' 
    genre_id = Column(Integer, primary_key=True) 
    genre_name = Column(String(25), nullable=False)

    def __init__ (self, genre_name=None): 
        self.genre_name = genre_name 

    def __repr__ (self):
        return('<Genre {} {}>'.format(self.genre_id, self.genre_name))


class Books(Base): 
    __tablename__ = 'books'
    book_id = Column(Integer, primary_key=True) 
    book_name = Column(String(255), nullable=False)
    book_description = Column(Text)

    def __init__ (self, book_name=None, book_description=None):
        self.book_name = book_name
        self.book_description = book_description

    def __repr__ (self):
        return('<Books {} {}>'.format(self.book_id, self.book_name))


class GenreBook(Base): 
    __tablename__ = 'genre_book'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    genre_id = Column(Integer, ForeignKey('genre.genre_id'))

    def __init__ (self, book_id=None, genre_id=None):
        self.book_id = book_id
        self.genre_id = genre_id

    def __repr__ (self):
        return('<GenreBook {} {}>'.format(self.book_id, self.genre_id))


class Autors(Base):
    __tablename__ = 'autors'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    book_id = Column(Integer, ForeignKey('books.book_id'))

    def __init__ (self, user_id=None, book_id=None):
        self.user_id = user_id
        self.book_id = book_id

    def __repr__ (self):
        return('<Autors {} {}>'.format(self.user_id, self.book_id))


class Chapters(Base): 
    __tablename__ = 'chapters'
    chapter_id = Column(Integer, primary_key=True) 
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False )
    chapter_number = Column(Integer, nullable=False) 
    chapter_title = Column(String(255))
    date_to_open = Column(DateTime)
    chapter_text = Column(Text)

    def __init__ (self, 
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

    def __repr__ (self):
        return('<Chapters {} {} {}>'.format(self.chapter_id, self.chapter_title, self.book_id))


class Grants(Base):
    __tablename__ = 'chapter_grants_allowed'
    id = Column(Integer,primary_key=True) 
    user_id = Column(Integer, ForeignKey('users.user_id'))  
    allowed_chapter_id = Column(Integer, ForeignKey('chapters.chapter_id'))

    def __init__ (self, user_id=None, allowed_chapter_id=None):
        self.user_id = user_id
        self.allowed_chapter_id = allowed_chapter_id 

    def __repr__ (self):
        return('<Grants {} {}>'.format(self.user_id, self.allowed_chapter_id))


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
