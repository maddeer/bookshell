#!/usr/bin/env python

import os.path
import sys
sys.path.insert(0, '../')

from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO, StringIO
from datetime import datetime, timedelta

from PyCRC.CRC32 import CRC32
from jinja2 import Template

from model.models import Book 

from .translit import transliterate 

def make_fb2_book(book):

    fb2zip = BytesIO()
    fb2text = StringIO()

    with open('templates/fb2.tmpl', 'r', encoding='utf-8') as template_file: 
        template = Template(template_file.read())

    fb2text.write(template.render(book=book,date=datetime.utcnow()))

    authors = ''
    for author in book['book_authors']: 
        authors += author.full_name.replace(' ', '_') + '_'

    crc32 = CRC32().calculate(fb2text.getvalue())
    file_name = '{}_{}_{}.fb2'.format(
                            authors,
                            book['book_data'].book_name.replace(' ', '_'),
                            crc32
                            )
    file_name = transliterate(file_name)

    with ZipFile(fb2zip, 'w', ZIP_DEFLATED) as myzip: 
        myzip.writestr(file_name, fb2text.getvalue()) 

    book_file = { 
               'file_name': file_name+'.zip',
               'file': fb2zip.getvalue(),
               'mimetype': 'application/x-zip-compressed-fb2',
               }
    return book_file 


if __name__ == '__main__': 
    book = Book()
    date = datetime.utcnow() - timedelta(days=10)
    book_info = book.get_book_info(book_id=1, user_id=2, date_now=date)
    book_file = make_fb2_book(book_info)

    with open(book_file['file_name'], "wb") as f:
        f.write(book_file['file'])

    print(book_file['file_name'])
    

