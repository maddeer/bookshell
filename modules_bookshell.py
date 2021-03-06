from datetime import datetime
import urllib.request
import re

import docx

from model.models import Genre, db_session, Book, GenreBook, Chapter
from model.models import Author, User


def docx_to_text(docx_file):
    with open(docx_file, 'rb') as f: 
        document = docx.Document(f)

    docText = '\n\n'.join([
        paragraph.text for paragraph in document.paragraphs
    ])
    return docText


def get_genre_dict():
    genre_dict = {}
    genre = Genre()
    for line in genre.get_all():
            genre_dict[line.genre_name.lower()] = line.id
    return genre_dict


def save_the_book(
        book_name,
        text,
        user_id,
        description='-',
        chapter_title='Chapter1',
        genre=[],
        time_open=datetime.now(),
        ):
    new_book = Book(
        book_name,
        description,
    )
    db_session.add(new_book)
    db_session.commit()
    genre_dict = get_genre_dict()
    if genre:
        for genre_id in genre:
            new_book_genre = GenreBook(new_book.id, genre_id)
            db_session.add(new_book_genre)
    if user_id:
        new_author = Author(user_id, new_book.id)
        db_session.add(new_author)
        db_session.commit()
        add_chapter(
            new_book.id,
            user_id,
            chapter_title,
            time_open,
            text,
            1,
            )
        return new_book.id
    else:
        return None


def add_chapter(
        book_id,
        user_id,
        chapter_title,
        time_open,
        text,
        chapter_number=None,
        ):
    author = Author.query.filter(
            Author.user_id == user_id
        ).filter(
            Author.book_id == book_id
        ).first()

    if author:
        new_chapter = Chapter(
            book_id,
            chapter_number,
            chapter_title,
            time_open,
            text,
        )
        db_session.add(new_chapter)
        db_session.commit()
        return new_chapter.id
    else:
        return None


def get_id_by_telegram_name(name):
    user = User.query.filter(User.telegram_login == name).first()
    if user is not None:
        return user.id
    else:
        return None


def get_text_from_google_doc(user_url):
    url = re.search(
        r'(https://docs\.google\.com/document/d/\S+)/edit',
        user_url
        )
    if url is None:
        return None
    url_to_download = url.group(1) + '/export?format=doc'
    file = urllib.request.urlopen(url_to_download)
    file_name = 'books/' + str(datetime.now()) + '_' + 'from_google' + '.docx'
    my_bytes = file.read()
    with open(file_name, 'wb') as file:
        file.write(my_bytes)
    my_text = docx_to_text(file_name)
    return my_text
