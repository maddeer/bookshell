from sqlalchemy import *
from migrate import *
from datetime import datetime

meta = MetaData()

about = Column('about', String(255))
last_edited = Column('last_edited', DateTime, default=datetime.utcnow)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)

    chapter_table = Table('chapter', meta, autoload=True)

    about.create(users_table)
    last_edited.create(chapter_table, populate_default=True)
    assert about is users_table.c.about
    assert last_edited is chapter_table.c.last_edited


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)
    chapter_table = Table('chapter', meta, autoload=True)
    chapter_table.c.last_edited.drop()
    users_table.c.about.drop()

