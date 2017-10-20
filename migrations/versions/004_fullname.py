from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from migrate import *

meta = MetaData()

full_name = Column('full_name', String(50))
first_name = Column('first_name', String(50))
middle_name = Column('middle_name', String(50))
last_name = Column('last_name', String(50))

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    db_session = scoped_session(sessionmaker(bind=meta.bind))
    users_table = Table('user', meta, autoload=True)
    first_name.create(users_table)
    middle_name.create(users_table)
    last_name.create(users_table)
    full_name_index = Index(
                            'ix_user_fullname',
                            users_table.c.first_name,
                            users_table.c.middle_name,
                            users_table.c.last_name,
                            )
    full_name_index.create()

    full_name_all = db_session.query(users_table).filter(users_table.c.full_name != None ).all()

    for name in full_name_all:
        update_fullname = users_table.update().values(
            first_name=name.full_name.split()[0],
            last_name=name.full_name.split()[-1],
            middle_name=' '.join(name.full_name.split()[1:-1]),
            ).where(users_table.c.id == name.id)
        meta.bind.execute(update_fullname)
        print(update_fullname)

    users_table.c.full_name.drop()

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    db_session = scoped_session(sessionmaker(bind=meta.bind))
    users_table = Table('user', meta, autoload=True)
    full_name.create(users_table)

    full_name_all = db_session.query(users_table).filter(users_table.c.full_name != None ).all()
    for name in full_name_all:
        update_fullname = users_table.update().values(
            full_name=' '.join([
                                name.first_name,
                                name.middle_name,
                                name.last_name
                              ]).replace('  ',' ').strip()
            ).where(users_table.c.id == name.id)
        meta.bind.execute(update_fullname)

    users_table.c.first_name.drop()
    users_table.c.last_name.drop()
    users_table.c.middle_name.drop()
