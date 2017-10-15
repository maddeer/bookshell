from datetime import datetime

import docx

from model.models import Genre, db_session, Book, GenreBook, Chapter, Author


def docx_to_text(docx_file):
    f = open(docx_file, 'rb')
    document = docx.Document(f)
    f.close()

    docText = '\n\n'.join([
        paragraph.text for paragraph in document.paragraphs
    ])
    return docText


def get_genre_dict():
    genre_dict = {}
    for line in Genre.query.all():
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
    if genre is not None:
        for book_genre in genre:
            new_book_genre = GenreBook(new_book.id, genre_dict[book_genre])
            db_session.add(new_book_genre)
    new_author = Author(user_id, new_book.id)
    db_session.add(new_author)
    db_session.commit()
    add_chapter(
        new_book.id,
        chapter_title,
        time_open,
        text,
        1,
        )
    return new_book.id


def add_chapter(
        book_id,
        chapter_title,
        time_open,
        text,
        chapter_number=None,
        ):
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
