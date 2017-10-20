from sqlalchemy import *
from migrate import *

meta = MetaData()

chapter_deleted = Column('deleted', SmallInteger)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    chapter_table = Table('chapter', meta, autoload=True)

    chapter_deleted.create(chapter_table)
    assert chapter_deleted is chapter_table.c.deleted

    update_chapter = chapter_table.update().values(deleted='0')
    meta.bind.execute(update_chapter)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    chapters_table = Table('chapter', meta, autoload=True)
    chapters_table.c.deleted.drop()
