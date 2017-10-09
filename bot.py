import logging
import re
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, ConversationHandler
from datetime import datetime
import magic
import configparser

#import modules_bookshell
from modules_bookshell import save_the_book, docx_to_text, get_genre_dict
from model.models import Genre, db_session, Book, GenreBook, Chapter, DATABASE_PATH

#DATABASE_PATH = 'bookshell.db'

config = configparser.ConfigParser()
config.sections()
config.read('conf/bookshell.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='log/bot.log',
)

MAIN_MENU, CREATE_A_BOOK, ADD_CHAPTER_NAME, ADD_A_GENRE, CHOSE_NAME,\
    CHOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_DESCRIPTION, SAVE_BOOK = range(10)

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
    Укажите название книги /chose_name
    Название первой главы /add_chap_name
    Напишите описние книги /add_description
    Загрузите текст книги или первой главы /upload_a_text
    ''', CREATE_A_BOOK],
    '/add_a_genre': ['''
    Укажите жанр
    ''', ADD_A_GENRE],
    '/chose_name': ['''
    Укажите название книги
    ''', CHOSE_NAME],
    '/chose_genres': ['''
    Выберете один или несколько жанров из предложенных,
    или укажите свой /add_a_genre
    Список жанров
    ''', CHOSE_GENRES],
    '/save_my_book': ['''
    Книга успещно добавленна
    ''', SAVE_MY_BOOK],
    '/add_chap_name': ['''
    Укажите название главы
    ''', ADD_CHAPTER_NAME],
    '/upload_a_text': ['''
    Перешлите мне содержимое главы в формате .docx
    Если вам нужно добавить еще главы,
    вы можете сделать это в режиме редактирование книги
    Спасибо!
    ''', UPLOAD_A_TEXT],
    '/add_description': ['''
    Введите описание книги
    ''', ADD_DESCRIPTION],
}


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start',
            command_react,
            pass_user_data=True)],
        states={
            MAIN_MENU: [
                CommandHandler(
                    'add_a_book',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'change_a_book',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'gind_a_book',
                    command_react,
                    pass_user_data=True)
            ],
            CREATE_A_BOOK: [
                CommandHandler(
                    'chose_genres',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'chose_name',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'add_chap_name',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'upload_a_text',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'add_description',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'save_my_book',
                    command_react,
                    pass_user_data=True),
                CommandHandler(
                    'save_my_book',
                    command_react,
                    pass_user_data=True),
            ],
            CHOSE_GENRES: [
                CommandHandler(
                    'add_a_genre',
                    command_react,
                    pass_user_data=True),
                MessageHandler(
                    Filters.text,
                    get_genres,
                    pass_user_data=True),
            ],
            ADD_A_GENRE: [
                MessageHandler(
                    Filters.text,
                    add_a_genre,
                    pass_user_data=True),
            ],
            CHOSE_NAME: [
                 MessageHandler(
                    Filters.text,
                    chose_name,
                    pass_user_data=True),
            ],
            ADD_DESCRIPTION: [
                 MessageHandler(
                    Filters.text,
                    add_description,
                    pass_user_data=True),
            ],
            ADD_CHAPTER_NAME: [
                 MessageHandler(
                    Filters.text,
                    add_chap_name,
                    pass_user_data=True),
            ],
            UPLOAD_A_TEXT: [
                MessageHandler(
                    Filters.document,
                    download_file,
                    pass_user_data=True),
            ],
        },
        fallbacks=[CommandHandler(
            'cancel',
            cancel,
            pass_user_data=True)]
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


def get_genres(bot, update, user_data):
    user_text = update.message.text
    user_data['genre'] = []
    genre_dict = get_genre_dict()
    user_genres = re.split(';|,', user_text)
    not_in_genre_list = []
    for user_genre in user_genres:
        if genre_dict.get(user_genre.lower()) is None:
            not_in_genre_list.append(user_genre)
    if not_in_genre_list == []:
        user_data['genre'] += user_genres
    else:
        update.message.reply_text(
            'Вы ввели жанры которых нет в списке {}'.format(
                not_in_genre_list
            )
        )
    update.message.reply_text(
        '''
        Вы выбрали следующие жанры {}
        '''.format(user_data['genre']))
    return CREATE_A_BOOK


def add_a_genre(bot, update, user_data):
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


def chose_name(bot, update, user_data):
    user_data['name'] = update.message.text
    return CREATE_A_BOOK


def add_description(bot, update, user_data):
    user_data['description'] = update.message.text
    return CREATE_A_BOOK


def add_chap_name(bot, update, user_data):
    user_data['chapter_name'] =\
        update.message.text
    return CREATE_A_BOOK


def command_react(bot, update, user_data):
    global ANSWERS
    answer = ANSWERS[update.message.text][0]
    if update.message.text == '/save_my_book':
        save_the_book(
            user_data.get('name'),
            user_data.get('text_from_file'),
            user_data.get('description'),
            user_data.get('chapter_name'),
            user_data.get('genre'))
    elif update.message.text == '/chose_genres':
        genre_dict = get_genre_dict()
        for line in genre_dict.keys():
            answer += line
            answer += ', '
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


def cancel(bot, update, user_data):
    user_data.clear()
    return ConversationHandler.END


if __name__ == "__main__":
    logging.info('bot started')
    main()
