import datetime
from databaseinit import db_session, Users, Chapters

datenow=datetime.datetime.now()
with open('../learnpython_lesson1/warandpeace2.txt', 'r', encoding='utf-8') as f:
    chapter = f.read()
    Chapter = Chapters(1,2,'II',datenow,chapter)
    db_session.add(Chapter)

db_session.commit()


