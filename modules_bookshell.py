import docx
from model.models import Genre, db_session, Book, GenreBook, Chapter
from datetime import datetime



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
        description='-',
        chapter_title='Chapter1',
        genre=[],
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
    new_chapter = Chapter(
        new_book.id,
        1,
        chapter_title,
        datetime.now(),
        text,
    )
    db_session.add(new_chapter)
    db_session.commit()