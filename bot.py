import logging
import re
import sys
from io import BytesIO
from datetime import datetime
import pickle


from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, ConversationHandler
from datetime import datetime
#import magic
import configparser
from sqlalchemy.orm import joinedload


from modules_bookshell import save_the_book, docx_to_text, get_genre_dict
from model.models import Genre, db_session, Book, GenreBook, Chapter, User, Author
from export.exporttopdf import make_pdf_book
from export.exporttofb2 import make_fb2_book
from tele_bot.modules import ANSWERS, make_conv_handler


config = configparser.ConfigParser()
config.sections()
config.read('conf/bookshell.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='log/bot.log',
)
MAIN_MENU, CREATE_A_BOOK, ADD_CHAPTER_NAME, ADD_A_GENRE, CHOOSE_NAME,\
    CHOOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_DESCRIPTION,\
    SAVE_BOOK, EDIT_A_BOOK, READ_A_BOOK, GET_BOOK_LIST_BY_AUTHOR,\
    GET_BOOK, BY_GENRE, BY_DATE, BY_NAME = range(17)

GENRE = {}


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    conv_handler = make_conv_handler(
        command_handler,
        Filters.text,
        get_genres,
        chooser_func,
        download_file,
        Filters.document,
        cancel,
        download_google_doc,
        get_book_list_by_author,
        get_book_list_by_genre,
        get_book,
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


def start(bot, update):
    if User.get_id_by_telegram_name(update.message.chat.username) is not None:
        anser = '''
        Добрый день!
        Вы находитесь в библиотеке.
        Вы можете добавить новую книгу /add_a_book
        или выбрать книгу для чтения /read_a_book
        для возврата в главное меню /start

        '''
        mode = MAIN_MENU
    else:
        answer = '''
        Добрый день! Вы не зарегестрированны,
        вам доступен только просмотр бесплатных книг
        Для просмотра книг нажмите /read_a_book
        для возврата в главное меню /start

        '''
        mode = MAIN_MENU_UN_REGISTRED
    update.message.reply_text(answer)
    return mode


def get_genres(bot, update, user_data):
    global ANSWERS
    user_text = update.message.text
    user_data['genre'] = []
    genre_dict = get_genre_dict()
    user_genres = re.split(';|,', user_text)
    not_in_genre_list = []
    user_genre_id_list = []
    for user_genre in user_genres:
        user_genre_id = genre_dict.get(user_genre.lower())
        if user_genre_id is None:
            not_in_genre_list.append(user_genre)
        else:
            user_genre_id_list.append(user_genre_id)
    if not_in_genre_list == []:
        user_data['genre'] += user_genre_id_list
    else:
        update.message.reply_text(
            'Вы ввели жанры которых нет в списке {}'.format(
                not_in_genre_list
            )
        )
    update.message.reply_text(
        '''
        Вы выбрали следующие жанры {}
        '''.format(user_genres))
    update.message.reply_text(ANSWERS['/add_a_book'][0])
    return ANSWERS['/add_a_book'][1]


def chooser_func(what, answer_to_user):
    def choose_inner(bot, update, user_data):
        user_data[what] = update.message.text
        update.message.reply_text(answer_to_user + update.message.text)
        update.message.reply_text(ANSWERS['/add_a_book'][0])
        return CREATE_A_BOOK
    return choose_inner


def get_book_file(book_id, book_name, format, user_id = 0 ):
    book = Book()
    book_info = book.get_book_info(book_id=book_id, user_id=user_id)
    if not book_info:
        return None
    if format == 'pdf':
        book_file = make_pdf_book(book_info)
    elif format == 'fb2':
        book_file = make_fb2_book(book_info)
    return book_file


def get_book(bot, update, user_data):
    author_id = None
    if user_data.get('selected_autrhor'):
        author_id = user_data['selected_autrhor']
        book_name = update.message.text
    else:
        book_name, user_name = update.message.text.split('|', maxsplit=1)
        author_obj = User.query.filter(User.user_name == user_name).first()
        if author_obj:
            author_id = author_obj.id
    if author_id:
        my_book = Author.query.filter(
            Author.user_id == author_id
            ).filter(
            Book.book_name == book_name
            ).options(
            joinedload(Author.books_author)).first(
            )
        if my_book:
            chat_id = update.message.chat.id
            user_id = User.get_id_by_telegram_name(update.message.chat.username)
            book_file = get_book_file(my_book.id, book_name, 'pdf', user_id)
            book_obj = BytesIO(book_file['file'])
            bot.send_document(
                chat_id=chat_id,
                document=book_obj,
                filename=book_file['file_name']
            )


def get_book_list_by_author(bot, update, user_data):
    user_text = update.message.text
    selected_autrhor = User.query.filter(User.user_name == user_text).first()
    if selected_autrhor:
        user_data['selected_autrhor'] = selected_autrhor.id
        author_id = selected_autrhor.id
        books_by_author = Author.query.filter(
            Author.user_id == author_id).options(
            joinedload(Author.books_author)).all()
        books_name = []
        for line in books_by_author:
            books_name.append(line.books_author.book_name)
        update.message.reply_text('книги автора: {} какую книгу выберете?'.format(
            books_name))
        return GET_BOOK
    else:
        update.message.reply_text(
            'Вы ошиблись с автором, повторите попытку')
        return GET_BOOK_LIST_BY_AUTHOR      


def get_book_list_by_genre(bot, update, user_data):
    user_text = update.message.text
    answer = 'выберете название книги и автора: \n'
    genres = user_text.split()
    for genre in genres:
        genre_obj = Genre.query.filter(Genre.genre_name == genre).first()
        if genre_obj:
            book_obj = Book()
            for line in book_obj.get_books_by_genre(genre_obj.id):
                answer += line.book_name + '|'
                book_id = line.id
                author = Author.query.filter(Author.book_id == book_id).first()
                if author:
                    author_name = User.query.filter(
                        User.id == author.user_id).first().user_name
                    answer += author_name + '\n'
    update.message.reply_text(answer)
    return GET_BOOK


def command_handler(bot, update, user_data):
    global ANSWERS
    answer = ANSWERS[update.message.text][0]
    if update.message.text == '/save_my_book':
        genre_dict = get_genre_dict()
        genres = []
        for genre in user_data.get('genre'):
            genres.append(genre_dict[genre])
        user_data['genre'] = genres
        save_the_book(
            user_data.get('name'),
            User.get_id_by_telegram_name(update.message.chat.username),
            user_data.get('text_from_file'),
            user_data.get('description'),
            user_data.get('chapter_name'),
            user_data.get('genre'))
    elif update.message.text == '/choose_genres':
        genre_dict = get_genre_dict()
        for line in genre_dict.keys():
            answer += line
            answer += ', '
    elif update.message.text == '/by_author':
        authors_id_list = Author.get_authors_with_books()
        for author_id in authors_id_list:
            answer += ' ' + User.query.filter(User.id == author_id).first().user_name
    elif update.message.text == '/by_genre':
        for line in Genre.get_parents():
            answer += line.genre_name + ' '
    elif update.message.text == '/start':
        if User.get_id_by_telegram_name(update.message.chat.username) is  None:
            answer = ANSWERS[update.message.text][2]
    update.message.reply_text(answer)
    return ANSWERS[update.message.text][1]


def download_file(bot, update, user_data):
    if user_data.get('name') is not None:
        user_file = bot.get_file(update.message.document.file_id)
        file_name = 'books/' + str(datetime.now()) + '_' +\
            update.message.chat.username + '.file'
        user_file.download(file_name)
        user_data['text_from_file'] =\
            docx_to_text(file_name)
        update.message.reply_text(
            '''Спасибо! Вы уверены что хотите добавить книгу на наш портал?
               Нажмите /save_my_book''')
        return CREATE_A_BOOK
    else:
        update.message.reply_text(
            '''
            Для записи книги, сначала необходимо выбрать название
            /choose_name
            ''')
        return CREATE_A_BOOK


def download_google_doc(bot, update, user_data):
    url = update.message.text
    if user_data.get('name') is not None:
        user_text = get_text_from_google_doc(url)
        if user_text is not None:
            user_data['text_from_file'] = user_text
            update.message.reply_text(
                '''Спасибо! Вы уверены что хотите добавить книгу на наш портал?
                   Нажмите /save_my_book''')
            return CREATE_A_BOOK
        else:
            update.message.reply_text(
                '''не верная ссылка, или нет доступа к файлу''')
            return UPLOAD_A_TEXT
    else:
        update.message.reply_text(
            '''Для записи книги, сначала необходимо выбрать название ''')
        return CREATE_A_BOOK


def cancel(bot, update, user_data):
    user_data.clear()
    return ConversationHandler.END


if __name__ == "__main__":
    logging.info('bot started')
    main()
