import logging
import re
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, ConversationHandler
from datetime import datetime
import magic
import configparser

from modules_bookshell import save_the_book, docx_to_text, get_genre_dict
from modules_bookshell import get_ig_by_tlegram_name
from tele_bot.modules import ANSWERS, make_conv_handler
from model.models import Genre, db_session, Book, GenreBook, Chapter, User

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
    CHOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_DESCRIPTION,\
    SAVE_BOOK, MAIN_MENU_UN_REGISTRED = range(11)

GENRE = {}


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    conv_handler = make_conv_handler(
        command_handler,
        Filters.text,
        get_genres,
        add_a_genre,
        chooser_func,
        download_file,
        Filters.document,
        cancel,
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


def chooser_func(what, answer_to_user):
    def choose_inner(bot, update, user_data):
        user_data[what] = update.message.text
        update.message.reply_text(answer_to_user + update.message.text)
        return CREATE_A_BOOK
    return choose_inner


def command_handler(bot, update, user_data):
    global ANSWERS
    answer = ANSWERS[update.message.text][0]
    if update.message.text == '/save_my_book':
        save_the_book(
            user_data.get('name'),
            get_ig_by_tlegram_name(update.message.chat.username),
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
