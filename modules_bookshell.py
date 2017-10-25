from datetime import datetime

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
            genre_dict[line.genre_name] = line.id
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
        for book_genre in genre:
            new_book_genre = GenreBook(new_book.id, book_genre)
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


def get_ig_by_tlegram_name(name):
    user = User.query.filter(User.telegram_login == name).first()
    if user is not None:
        return user.id
    else:
        return None
