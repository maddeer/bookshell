import csv
from sqlalchemy import *
from migrate import *

meta = MetaData()

genre = []
with open('genre', 'r', encoding='utf-8') as f:
    fields = ["ID","Name"]
    csvdata = csv.DictReader(f, fields, delimiter=';')
    for row in csvdata:
        genre.append(row)

genre_name_type = Column('genre_name_type',String(50),) # nullable=False)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    genre_table = Table('genre', meta, autoload=true)

    genre_name_type.create(genre_table)
    assert genre_name_type is genre_table.c.genre_name_type

    update_genre = genre_table.update().values(genre_name_type=genre_table.c.genre_name)
    meta.bind.execute(update_genre)

    genre_name_type.alter(nullable=False)

    genre_index = Index('ix_genre_genre', genre_table.c.genre_name, unique=True)
    genre_index.create()

    [ meta.bind.execute(genre_table.insert().values(genre_name=row['Name'],genre_name_type=row['ID'])) for row in genre ]

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    genre_table = Table('genre', meta, autoload=true)
    Index('ix_genre_genre',genre_table.c.genre_name, unique=True).drop()
    genre_table.c.genre_name_type.drop()
    

