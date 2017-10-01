import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
import magic
import configparser

import modules_bookshell


config = configparser.ConfigParser()
config.sections()
config.read('bookshell_bot.conf')
TELEGRAMM_KEY = config['DEFAULT']['TELEGRAMM_KEY']


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
)

#BOT_MOD = {}

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
    Выберете один или несколько жанров книги(через запятую),
    если нужного жанра нет в списке, выберете /add_a_genre
    после выбора жанров выберете /chose_a_name
    ''',
    '/add_a_genre':
    '''
    Укажите жанр книги
    ''',
    '/chose_a_name':
    '''
    Укажите название книги
    '''
}


def main():
    updater = Updater(TELEGRAMM_KEY)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler(['start', 'add_a_genre','add_a_book', 'chose_a_name'], answer_to_user))
    dp.add_handler(MessageHandler(Filters.text, reply_bot))
    dp.add_handler(MessageHandler(Filters.document, download_file))
    updater.start_polling()
    updater.idle()




def reply_bot(bot, update):
    global BOT_MOD
    pass


def answer_to_user(bot, update):
    global ANSWERS
    global BOT_MOD

    BOT_MOD[update.message.chat.username]= update.message.text
    update.message.reply_text(ANSWERS[update.message.text])


def download_file(bot, update):
    #print(update.message.document)
    user_file = bot.get_file(update.message.document.file_id)
    file_name = str(datetime.now()) + '_' + update.message.chat.username + '.file'
    user_file.download(file_name)
    print(magic.from_file(file_name))
    text_from_file = modules_bookshell.docx_to_text(file_name)
    print(text_from_file)
    # if magic.from_file(file_name) == 'Microsoft Word 2007+':
    #     text_from_file = modules_bookshell.docx_to_text(file_name)
    #     print(text_from_file)

if __name__ == "__main__":
    logging.info('bot started')
    main()
