import logging
import re
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, ConversationHandler
from datetime import datetime
import magic
import configparser

import modules_bookshell
from model.models import Genre, db_session, Book, GenreBook, Chapter


config = configparser.ConfigParser()
config.sections()
config.read('conf/bookshell.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='log/bot.log',
)

MAIN_MENU, CREATE_A_BOOK, ADD_CHAPTER_NAME, ADD_NEW_GENRE, CHOSE_A_NAME,\
    CHOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_BOOK_DESCRIPTION = range(9)

NEW_BOOK = {}
GENRE = {}
ANSWERS = {
    '/start': ['''
    Добрый день!
    Вы находитесь в библиотеке.
    Вы можете добавить новую книгу /add_a_book
    Отредактирвать старую /change_a_book
    или выбрать книгу для чтения /chose_a_book
    ''', MAIN_MENU],
    '/add_a_book': ['''
    Выберете один или несколько жанров книги, /chose_genres
    Укажите название книги /chose_a_name
    Название первой главы /add_a_chapter_name
    Напишите описние книги /add_book_description
    Загрузите текст книги или первой главы /upload_a_text
    ''', CREATE_A_BOOK],
    '/add_new_genre': ['''
    Укажите жанр
    ''', ADD_NEW_GENRE],
    '/chose_a_name': ['''
    Укажите название книги
    ''', CHOSE_A_NAME],
    '/chose_genres': ['''
    Выберете один или несколько жанров из предложенных,
    или укажите свой /add_a_genre

    Список жанров
    ''', CHOSE_GENRES],
    '/safe_my_book': ['''
    Книга успещно добавленна
    ''', SAVE_MY_BOOK],
    '/add_chapter_name': ['''
    Укажите название главы
    ''', ADD_CHAPTER_NAME],
    '/upload_a_text': ['''
    Перешлите мне содержимое главы в формате .docx
    Если вам нужно добавить еще главы,
    вы можете сделать это в режиме редактирование книги
    Спасибо!

    ''', UPLOAD_A_TEXT],
    '/add_book_description': ['''
    Введите описание книги
    ''', ADD_BOOK_DESCRIPTION],

}


def get_genre_dict():
    genre_dict = {}
    for line in Genre.query.all():
            genre_dict[line.genre_name] = line.id
    return genre_dict


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', answer_to_user_command)],
        states={
            MAIN_MENU: [
                CommandHandler('add_a_book', answer_to_user_command),
                CommandHandler('change_a_book', answer_to_user_command),
                CommandHandler('gind_a_book', answer_to_user_command)
            ],
            CREATE_A_BOOK: [
                CommandHandler('chose_genres', answer_to_user_command),
                CommandHandler('chose_a_name', answer_to_user_command),
                CommandHandler('add_a_chapter_name', answer_to_user_command),
                CommandHandler('upload_a_text', answer_to_user_command),
                CommandHandler('add_book_description', answer_to_user_command),
                CommandHandler('save_my_book', answer_to_user_command),
            ],
            CHOSE_GENRES: [
                CommandHandler('add_new_genre', answer_to_user_command),
                MessageHandler(Filters.text, get_genres),
            ],
            ADD_NEW_GENRE: [
                MessageHandler(Filters.text, add_new_genre),
            ],
            CHOSE_A_NAME: [
                 MessageHandler(Filters.text, chose_a_name),
            ],
            ADD_BOOK_DESCRIPTION: [
                 MessageHandler(Filters.text, add_book_description),
            ],
            ADD_CHAPTER_NAME: [
                 MessageHandler(Filters.text, add_chapter_name),
            ],
            UPLOAD_A_TEXT: [
                MessageHandler(Filters.document, download_file),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


def start(bot, update):
    anser = '''
    Добрый день!
    Вы находитесь в библиотеке.
    Вы можете добавить новую книгу /add_a_book
    Отредактирвать старую /change_a_book
    или выбрать книгу для чтения /chose_a_book
    '''
    update.message.reply_text(answer)

    return MAIN_MENU


def get_genres(bot, update):
    user_text = update.message.text
    NEW_BOOK[update.message.chat.username]['genre'] = []
    genre_dict = get_genre_dict()
    user_genres = re.split(';|,', user_text)
    not_in_genre_list = []
    for user_genre in user_genres:
        if genre_dict.get(user_genre.lower()) is None:
            not_in_genre_list.append(user_genre)
    if not_in_genre_list == []:
        NEW_BOOK[update.message.chat.username]['genre'] += user_genres
    else:
        update.message.reply_text(
            'Вы ввели жанры которых нет в списке {}'.format(
                not_in_genre_list
            )
        )
    update.message.reply_text(
        '''
        Вы выбрали следующие жанры {}
        '''.format(NEW_BOOK[update.message.chat.username]['genre']))
    return CREATE_A_BOOK


def add_new_genre(bot, update):
    user_text = update.message.text
    genre_dict = get_genre_dict()
    if user_text not in genre_dict.keys():
        new_genre = Genre(user_text.lower())
        db_session.add(new_genre)
        db_session.commit()
        update.message.reply_text(
            '''
            Жанр добавлен в базу,
            Если хотиле выбраь его для книги, пожалуйста нпишите еще раз
            если хотите добавить новый жанр, выберете /add_a_genre
            ''')
    return CHOSE_GENRES


def chose_a_name(bot, update):
    NEW_BOOK[update.message.chat.username]['name'] = update.message.text
    return CREATE_A_BOOK


def add_book_description(bot, update):
    NEW_BOOK[update.message.chat.username]['description'] = update.message.text
    return CREATE_A_BOOK


def add_chapter_name(bot, update):
    NEW_BOOK[update.message.chat.username]['chapter_name'] =\
        update.message.text
    return CREATE_A_BOOK


def answer_to_user_command(bot, update):
    global ANSWERS
    global NEW_BOOK
    if NEW_BOOK.get(update.message.chat.username) is None:
        NEW_BOOK[update.message.chat.username] = {}
    answer = ANSWERS[update.message.text][0]
    if update.message.text == '/safe_my_book':
        safe_the_book(
            NEW_BOOK[update.message.chat.username]['name'],
            NEW_BOOK[update.message.chat.username]['text_from_file'],
            NEW_BOOK[update.message.chat.username]['description'],
            NEW_BOOK[update.message.chat.username]['chapter_name'],
            NEW_BOOK[update.message.chat.username]['genre'],
        )
    elif update.message.text == '/chose_genres':
        genre_dict = get_genre_dict()
        for line in genre_dict.keys():
            answer += line
            answer += ', '
    update.message.reply_text(answer)
    return ANSWERS[update.message.text][1]


def download_file(bot, update):
    global NEW_BOOK
    if NEW_BOOK[update.message.chat.username].get('name') is not None:
        user_file = bot.get_file(update.message.document.file_id)
        file_name = 'books/' + str(datetime.now()) + '_' +\
            update.message.chat.username + '.file'
        user_file.download(file_name)
        NEW_BOOK[update.message.chat.username]['text_from_file'] =\
            modules_bookshell.docx_to_text(file_name)
        update.message.reply_text(
            '''Спасибо! Вы уверены что хотите добавить книгу на наш портал?
               Нажмите /save_my_book''')
    return MAIN_MENU


def cancel(bot, update):
    return ConversationHandler.END


if __name__ == "__main__":
    logging.info('bot started')
    main()
