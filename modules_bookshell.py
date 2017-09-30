import docx


from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def docx_to_text(docx_file):
    f = open('docx_file', 'rb')
    document = docx.Document(f)
    f.close()

    docText = '\n\n'.join([
        paragraph.text for paragraph in document.paragraphs
    ])
    return docText


def connect_to_db(db_name):
    engine = create_engine('sqlite:///blog.sqlite')
    db_session = scoped_session(sessionmaker(bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()
    
class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String(255) unique=True)
    full_name = Column(String(255))
    role = Column(Integer)
    password = Column(String(255), unique=True)

    def __init__(self, user_name=None, full_name=None, role = None, password=None):
        self.user_name = user_name
        self.full_name = full_name
        self.password = password
        self.role = role
        self.email = email

    def __repr__(self):
        return '<User {} {}>'.format(self.user_name, self.role)

class 
