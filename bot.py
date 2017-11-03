import logging
import re
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, ConversationHandler
from datetime import datetime
import magic
import configparser

from modules_bookshell import save_the_book, docx_to_text, get_genre_dict
from tele_bot.modules import ANSWERS, make_conv_handler
from model.models import Genre, db_session, Book, GenreBook, Chapter, User
from io import BytesIO
from export.exporttopdf import make_pdf_book
#from export.exporttofb2 import make_fb2_book




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
    SAVE_BOOK, MAIN_MENU_UN_REGISTRED = range(11)

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
        get_book,
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


def start(bot, update):
    if get_ig_by_tlegram_name(update.message.chat.username) is not None:
        anser = '''
        Добрый день!
        Вы находитесь в библиотеке.
        Вы можете добавить новую книгу /add_a_book
        Отредактирвать старую /change_a_book
        или выбрать книгу для чтения /find_a_book
        '''
        mode = MAIN_MENU
    else:
        answer = '''
        Добрый день! Вы не зарегестрированны,
        вам доступен только просмотр бесплатных книг
        Для регистрации выберете /registation
        Для просмотра книг /find_a_book
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
        pass
        #book_file = make_fb2_book(book_info)
    return book_file


def get_book(bot, update, user_data):
    user_text = update.message.text.lower()
    if user_data['selected_autrhor']:
        my_book = Author.query.filter(
            Author.user_id == user_data['selected_autrhor']
            ).filter(
            Author.books_author.books_name == user_text
            ).options(
            joinedload(Author.books_author)).first(
            )
        if my_book:
            chat_id = bot.get_updates()[-1].message.chat_id
            user_id = User.get_ig_by_tlegram_name(update.message.chat.username)
            book_obj = get_book_file(my_book.id, user_text, 'pdf', user_id)
            bot.send_document(chat_id=chat_id, document=book_obj)



def get_book_list_by_author(bot, update, user_data):
    user_data['author_list'] = []
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
            User.get_ig_by_tlegram_name(update.message.chat.username),
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
        authors_id_list = Author.get_authors_id()
        for author_id in authors_id_list:
            answer += ' ' + User.query.filter(User.id == author_Id).first().user_name
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
