from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler

MAIN_MENU, CREATE_A_BOOK, ADD_CHAPTER_NAME, ADD_A_GENRE, CHOOSE_NAME,\
    CHOOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_DESCRIPTION,\
    SAVE_BOOK, EDIT_A_BOOK, READ_A_BOOK, GET_BOOK_LIST_BY_AUTHOR,\
    GET_BOOK, BY_GENRE, BY_DATE, BY_NAME = range(17)

ANSWERS = {
    '/start': ['''
    Добрый день!
    Вы находитесь в библиотеке.
    Вы можете добавить новую книгу /add_a_book
    Отредактирвать старую /edit_a_book
    или выбрать книгу для чтения /read_a_book
    ''', MAIN_MENU],
    '/add_a_book': ['''
    Укажите название книги /choose_name
    Выберете жанр книги, /choose_genres
    Название первой главы /add_chap_name
    Напишите описние книги /add_description
    Загрузите текст книги или первой главы /upload_a_text
    ''', CREATE_A_BOOK],
    '/choose_name': ['''
    Укажите название книги
    ''', CHOOSE_NAME],
    '/choose_genres': ['''
    Выберете жанры,
    Список жанров
    ''', CHOOSE_GENRES],
    '/save_my_book': ['''
    Книга успещно добавленна
    ''', SAVE_MY_BOOK],
    '/add_chap_name': ['''
    Укажите название главы
    ''', ADD_CHAPTER_NAME],
    '/upload_a_text': ['''
    Перешлите содержимое главы в формате .docx
    или напишите ссылку на google doc
    Если вам нужно добавить еще главы,
    вы можете сделать это в режиме редактирование книги
    Спасибо!
    ''', UPLOAD_A_TEXT],
    '/add_description': ['''
    Введите описание книги
    ''', ADD_DESCRIPTION],
    '/edit_a_book': ['''
    Выберете книгу, которую хотите отредактировать
    ''', EDIT_A_BOOK],
    '/read_a_book': ['''
    По каким параметрам хотите выбрать книгу
    по автору /by_author
    по жанру /by_genre
    по дате добавления /by_date
    по названию /by_name
    ''', READ_A_BOOK],
    '/by_author': ['''
    Выберете автора
    ''', GET_BOOK_LIST_BY_AUTHOR],
    '/by_genre': ['''
    Выберете жанр
    ''', BY_GENRE],
    '/by_date': ['''
    Послежние 10 книг
    если хотите еще 10 выберете /more_10
    ''', BY_DATE],
    '/by_name': ['''
    Укажите название книги
    ''', BY_NAME],
}


def make_conv_handler(
        command_handler,
        filters_text,
        get_genres,
        chooser_func,
        download_file,
        filters_document,
        cancel,
        download_google_doc,
        get_book_list_by_author,
        get_book,
        ):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            'start',
            command_handler,
            pass_user_data=True)],
        states={
            MAIN_MENU: [
                CommandHandler(
                    'add_a_book',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'edit_a_book',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'read_a_book',
                    command_handler,
                    pass_user_data=True)
            ],
            CREATE_A_BOOK: [
                CommandHandler(
                    'choose_genres',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'choose_name',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'add_chap_name',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'upload_a_text',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'add_description',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'save_my_book',
                    command_handler,
                    pass_user_data=True),
            ],
            CHOOSE_GENRES: [
                MessageHandler(
                    filters_text,
                    get_genres,
                    pass_user_data=True),
            ],
            CHOOSE_NAME: [
                 MessageHandler(
                    filters_text,
                    chooser_func(
                        'name',
                        'Вы выбрали имя книги ',
                        ),
                    pass_user_data=True),
            ],
            ADD_DESCRIPTION: [
                 MessageHandler(
                    filters_text,
                    chooser_func(
                        'description',
                        'Вы выбрали описание книги '
                        ),
                    pass_user_data=True),
            ],
            ADD_CHAPTER_NAME: [
                 MessageHandler(
                    filters_text,
                    chooser_func(
                        'chapter_name',
                        'Вы выбрали название главы '
                        ),
                    pass_user_data=True),
            ],
            UPLOAD_A_TEXT: [
                MessageHandler(
                    filters_document,
                    download_file,
                    pass_user_data=True),
                MessageHandler(
                    filters_text,
                    download_google_doc,
                    pass_user_data=True),
            ],
            READ_A_BOOK: [
                MessageHandler(
                    'by_author',
                    command_handler,
                    pass_user_data=True),
            ],
            GET_BOOK_LIST_BY_AUTHOR: [
                MessageHandler(
                    filters_text,
                    get_book_list_by_author,
                    pass_user_data=True),
            ],
            GET_BOOK: [
                MessageHandler(
                    filters_text,
                    get_book,
                    pass_user_data=True),
            ],
        },
        fallbacks=[CommandHandler(
            'cancel',
            cancel,
            pass_user_data=True)]
    )
    return conv_handler
