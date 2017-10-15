from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import ConversationHandler

MAIN_MENU, CREATE_A_BOOK, ADD_CHAPTER_NAME, ADD_A_GENRE, CHOSE_NAME,\
    CHOSE_GENRES, SAVE_MY_BOOK, UPLOAD_A_TEXT, ADD_DESCRIPTION,\
    SAVE_BOOK = range(10)

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


def make_conv_handler(
        command_handler,
        filters_text,
        get_genres,
        add_a_genre,
        chooser_func,
        download_file,
        filters_document,
        cancel,
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
                    'change_a_book',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'gind_a_book',
                    command_handler,
                    pass_user_data=True)
            ],
            CREATE_A_BOOK: [
                CommandHandler(
                    'chose_genres',
                    command_handler,
                    pass_user_data=True),
                CommandHandler(
                    'chose_name',
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
                CommandHandler(
                    'save_my_book',
                    command_handler,
                    pass_user_data=True),
            ],
            CHOSE_GENRES: [
                CommandHandler(
                    'add_a_genre',
                    command_handler,
                    pass_user_data=True),
                MessageHandler(
                    filters_text,
                    get_genres,
                    pass_user_data=True),
            ],
            ADD_A_GENRE: [
                MessageHandler(
                    filters_text,
                    add_a_genre,
                    pass_user_data=True),
            ],
            CHOSE_NAME: [
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
            ],
        },
        fallbacks=[CommandHandler(
            'cancel',
            cancel,
            pass_user_data=True)]
    )
    return conv_handler
