import datetime
from models import db_session, Chapter

datenow=datetime.datetime.now()
with open('../learnpython_lesson1/warandpeace2.txt', 'r', encoding='utf-8') as f:
    chapter = f.read()
    chapter_txt = Chapter(1,2,'II',datenow,chapter)
    db_session.add(chapter_txt)

with open('../learnpython_lesson1/warandpeace.txt', 'r', encoding='utf-8') as f:
    chapter = f.read()
    chapter_txt = Chapter(1,1,'I',datenow,chapter)
    db_session.add(chapter_txt)

db_session.commit()


