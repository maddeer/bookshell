from sqlalchemy import *
from migrate import *

meta = MetaData()



def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)
    telegram_id = Column('telegram_id', Integer)
    telegram_id.create(users_table)


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)
    users_table.c.telegram_id.drop()
