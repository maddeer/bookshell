import logging
import re
import sys
sys.path.insert(0, '../')

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import magic
import configparser

import modules_bookshell
from databaseinit import Genre, db_session



config = configparser.ConfigParser()
config.sections()
config.read('bot.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='../log/bot.log',
)

BOT_MOD = {}
NEW_BOOK = {}
#ANSWERS = {}

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
    Выберете один или несколько жанров книги,
    если нужного жанра нет в списке, напишите /add_a_genre
    после выбора жанров напишите /chose_a_name
    доступные жанры: 
    ''',
    '/add_a_genre':
    '''
    Укажите жанр 
    ''',
    '/chose_a_name':
    '''
    Укажите название книги
    ''',
    '/chose_a_genre':
    '''
    Выберете один или несколько жанров из предложенных, или укажите свой. 
    '''
}
genre = Genre


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler([
        'start',
        'add_a_genre',
        'add_a_book', 
        'chose_a_name', 
        'chose_a_genre',
        ], answer_to_user))
    dp.add_handler(MessageHandler(Filters.text, reply_bot))
    dp.add_handler(MessageHandler(Filters.document, download_file))
    updater.start_polling()
    updater.idle()


def reply_bot(bot, update):
    global BOT_MOD
    global NEW_BOOK
    user_text = update.message.text
    if BOT_MOD[update.message.chat.username] == '/add_a_book':
        NEW_BOOK[update.message.chat.username]['genre'].append(re.split(';|,',update.message.reply_text(answer)))
    elif BOT_MOD[update.message.chat.username] == '/add_a_genre':
        new_genre = Genre(user_text)
        db_session.add(new_genre)
        db_session.commit()
    elif BOT_MOD[update.message.chat.username] == '/chose_a_name':
        NEW_BOOK[update.message.chat.username]['name'] = reply_text(answer)
        update.message.reply_text('А теперь загрузите книгу')


def answer_to_user(bot, update):
    global ANSWERS
    global BOT_MOD
    global NEW_BOOK
    answer = ANSWERS[update.message.text]
    if update.message.text == '/add_a_book':
        for line in genre.query.all():
            answer += line.genre_name
            answer += ', '
            NEW_BOOK[update.message.chat.username] = {}

    update.message.reply_text(answer)
    BOT_MOD[update.message.chat.username] = update.message.text


def download_file(bot, update):
    #print(update.message.document)
    if BOT_MOD[update.message.chat.username] == '/upload_a_book' and \
        NEW_BOOK[update.message.chat.username]['name'] is not None:

        user_file = bot.get_file(update.message.document.file_id)
        file_name = str(datetime.now()) + '_' + update.message.chat.username + '.file'
        user_file.download(file_name)
        #print(magic.from_file(file_name))
        text_from_file = modules_bookshell.docx_to_text(file_name)


    #print(text_from_file)
    #if 
    # if magic.from_file(file_name) == 'Microsoft Word 2007+':
    #     text_from_file = modules_bookshell.docx_to_text(file_name)
    #     print(text_from_file)

if __name__ == "__main__":
    logging.info('bot started')
    main()
