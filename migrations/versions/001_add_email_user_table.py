from sqlalchemy import *
from migrate import *

meta = MetaData()

user_email = Column('email', String(255)) #, unique=True, index=True, nullable=False)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)

    user_email.create(users_table)
    assert user_email is users_table.c.email

    update_email = users_table.update().values(email=users_table.c.user_name+'@email.com')
    meta.bind.execute(update_email)

    user_email.alter(nullable=False)

    email_index = Index('ix_user_email', users_table.c.email, unique=True)
    email_index.create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    meta.bind = migrate_engine
    users_table = Table('user', meta, autoload=True)
    users_table.c.email.drop()
