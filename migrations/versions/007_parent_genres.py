import csv

from sqlalchemy import *
from migrate import *

meta = MetaData()

genre = []
with open('genre', 'r', encoding='utf-8') as f:
    fields = ["ID","Name","parent"]
    csvdata = csv.DictReader(f, fields, delimiter=';')
    for row in csvdata:
        genre.append(row)

genre_parent = Column('parent',Integer, ForeignKey('genre.id')) 

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    genre_table = Table('genre', meta, autoload=true)

    genre_parent.create(genre_table)
    assert genre_parent is genre_table.c.parent

    try:
        Index('ix_genre_genre',genre_table.c.genre_name, unique=True).drop()
    except sqlalchemy.exc.NotSupportedError:
        pass
    genre_index = Index('ix_genre_genre', genre_table.c.genre_name)
    genre_index.create()

    meta.bind.execute(genre_table.delete())
    [ meta.bind.execute( genre_table.insert().values(
                                genre_name=row['Name'],
                                genre_name_type=row['ID'],
                                parent=row['parent'],
                                )) for row in genre ]

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    genre_table = Table('genre', meta, autoload=true)
    genre_table.c.parent.drop()
