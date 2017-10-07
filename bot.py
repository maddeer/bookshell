import logging
import re
import sys

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import magic
import configparser

import modules_bookshell
from models import Genre, db_session, DB_PATH, Book, GenreBook, Chapter


config = configparser.ConfigParser()
config.sections()
config.read('conf/bot.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']
DB_PATH = config['DEFAULT']['DB_PATH']
DB_PATH = 'sqlite:///' + DB_PATH

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='log/bot.log',
)


BOT_MOD = {}
NEW_BOOK = {}
GENRE = {}
ANSWERS = {
    '/start':
    '''
    Добрый день!
    Вы находитесь в библиотеке.
    Вы можете добавить новую книгу /add_a_book
    Отредактирвать старую /change_a_book
    или выбрать книгу для чтения /chose_a_book
    ''',
    '/add_a_book':
    '''
    Выберете один или несколько жанров книги, /chose_genres
    Укажите название книги /chose_a_name
    Название первой главы /add_a_chapter_name
    Напишите описние книги /add_book_description
    и после этого загрузите главу или книгу /upload_an_article
    ''',
    '/add_a_genre':
    '''
    Укажите жанр
    ''',
    '/chose_a_name':
    '''
    Укажите название книги
    ''',
    '/chose_genres':
    '''
    Выберете один или несколько жанров из предложенных,
    или укажите свой /add_a_genre

    Список жанров
    ''',
    '/safe_my_book':
    '''
    Книга успещно добавленна
    ''',
    '/add_a_chapter_name':
    '''
    Укажите название главы
    ''',
    '/upload_an_article':
    '''
    Перешлите мне содержимое главы в формате .docx
    Если вам нужно добавить еще главы,
    вы можете сделать это в режиме редактирование книги
    Спасибо!

    ''',

}


def get_genre_dict():
    genre_dict = {}
    for line in Genre.query.all():
            genre_dict[line.genre_name] = line.id
    return genre_dict


def safe_the_book(
        book_name,
        text,
        description='-',
        chapter_title='Chapter1',
        genre=[],
        ):
    new_book = Book(
        name,
        description,
    )
    db_session.add(new_book)
    db_session.commit()
    genre_dict = get_genre_dict()
    for book_genre in genre:
        new_book_genre = GenreBook(new_book.id, genre_dict[book_genre])
        db_session.add(new_book_genre)
    new_chapter = Chapter(
        new_book.id,
        1,
        chapter_title,
        datetime.now(),
        text_from_file,
    )
    db_session.add(new_chapter)
    db_session.commit()


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler([
        'start',
        'add_a_genre',
        'add_a_book',
        'chose_a_name',
        'chose_genres',
        'safe_my_book',
        'add_a_chapter_name',
        'upload_an_article'
        ], answer_to_user_command))
    dp.add_handler(MessageHandler(Filters.text, reply_bot))
    dp.add_handler(MessageHandler(Filters.document, download_file))
    updater.start_polling()
    updater.idle()


def reply_bot(bot, update):
    global BOT_MOD
    global NEW_BOOK
    user_text = update.message.text
    if BOT_MOD[update.message.chat.username] == '/chose_genres':
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
    elif BOT_MOD[update.message.chat.username] == '/add_a_genre':
        genre_dict = get_genre_dict()
        if user_text not in genre_dict.keys():
            new_genre = Genre(user_text.lower())
            db_session.add(new_genre)
            db_session.commit()
            update.message.reply_text('''
            Жанр добавлен в базу,
            если хотите добавить его к книге, выберете /chose_genres
            ''')
    elif BOT_MOD[update.message.chat.username] == '/chose_a_name':
        NEW_BOOK[update.message.chat.username]['name'] = user_text
    elif BOT_MOD[update.message.chat.username] == '/add_book_description':
        NEW_BOOK[update.message.chat.username]['description'] = user_text
        update.message.reply_text('название первой главы')
    elif BOT_MOD[update.message.chat.username] == '/add_a_chapter_name':
        NEW_BOOK[update.message.chat.username]['chapter_title'] = user_text
        update.message.reply_text('''
            А перешлите мне содержимое главы в формате .docx
            Если вам нужно добавить еще главы,
            вы можете сделать это в режиме редактирование книги
            Спасибо!
            ''')


def answer_to_user_command(bot, update):
    global ANSWERS
    global BOT_MOD
    global NEW_BOOK
    if NEW_BOOK.get(update.message.chat.username) is None:
        NEW_BOOK[update.message.chat.username] = {}
    answer = ANSWERS[update.message.text]
    BOT_MOD[update.message.chat.username] = update.message.text
    if update.message.text == '/safe_my_book':
        safe_the_book(
            NEW_BOOK[update.message.chat.username]['name'],
            NEW_BOOK[update.message.chat.username]['text_from_file'],
            NEW_BOOK[update.message.chat.username]['description'],
            NEW_BOOK[update.message.chat.username]['chapter_title'],
            NEW_BOOK[update.message.chat.username]['genre'],
        )
    elif update.message.text == '/chose_genres':
        genre_dict = get_genre_dict()
        for line in genre_dict.keys():
            answer += line
            answer += ', '
    update.message.reply_text(answer)
    BOT_MOD[update.message.chat.username] = update.message.text


def download_file(bot, update):
    global BOT_MOD
    global NEW_BOOK
    if BOT_MOD[update.message.chat.username] == '/upload_an_article' and \
            NEW_BOOK[update.message.chat.username].get('name') is not None:
        user_file = bot.get_file(update.message.document.file_id)
        file_name = 'books/' + str(datetime.now()) + '_' +\
            update.message.chat.username + '.file'
        user_file.download(file_name)
        NEW_BOOK[update.message.chat.username]['text_from_file'] =\
            modules_bookshell.docx_to_text(file_name)
        update.message.reply_text(
            '''Спасибо! Вы уверены что хотите добавить книгу на наш портал?
               Нажмите /safe_my_book''')


if __name__ == "__main__":
    logging.info('bot started')
    main()
