import os.path
import sys
sys.path.insert(0, '../')

from io import BytesIO

from datetime import datetime, timedelta

from PyCRC.CRC32 import CRC32

from .pdfclass import PDF 
from model.models import Book
from .translit import transliterate 


def make_pdf_book(book): 
    pdf = PDF()

    base = os.path.abspath(os.path.dirname(__file__))
    font_dir = os.path.join(base, 'font')

    arial = os.path.join(font_dir, 'LiberationSans-Regular.ttf')
    arial_bold = os.path.join(font_dir, 'LiberationSans-Bold.ttf')
    times = os.path.join(font_dir, 'LiberationSerif-Regular.ttf')

    pdf.add_font('Arial', '', arial, uni=True)
    pdf.add_font('Arial-Bold', '', arial_bold, uni=True)
    pdf.add_font('Times', '', times, uni=True)
    pdf.alias_nb_pages()

    pdf.book_name = book['book_data'].book_name
    pdf.set_title(pdf.book_name)

    authors = ''
    for author in book['book_authors']: 
        pdf.set_author('BookShell 0.1')
        authors += author.full_name.replace(' ', '_') + '_'

    pdf.title_page(book['book_authors'], pdf.book_name)
    pdf.add_page()

    if book['book_data'].book_description: 
        pdf.chapter_body(book['book_data'].book_description)

    book_text = ''
    for chapter in book['book_chapters']:
        pdf.title = chapter[0].chapter_title

        if chapter[1] == 'allow':
            chapter_txt=chapter[0].chapter_text 
        else:
            deny ="""\n\nДанная глава закрыта для доступа автором. 
Глава будет доступна для бесплатного просмотра {}"""
            deny = deny.format(chapter[0].date_to_open.strftime('%d-%m-%Y'))
            chapter_txt = chapter[0].short_text + deny

        pdf.print_chapter(chapter[0].chapter_number, chapter[0].chapter_title, chapter_txt)
        book_text += chapter[0].chapter_text

    crc32 = CRC32().calculate(book_text)
    pdf_file_name = '{}_{}_{}.pdf'.format(authors, pdf.book_name.replace(' ', '_'), crc32)
    pdf_file_name = transliterate(pdf_file_name)
    #pdf_file_name = os.path.join('static', 'pdf', pdf_file_name)

    with BytesIO() as pdf_file: 
        pdf_file.write(pdf.output(dest='S').encode('latin-1'))

        book_file = { 
                   'pdf_file_name': pdf_file_name,
                   'pdf_file': pdf_file.getvalue(),
                   'mimetype': 'application/pdf',
                   }
        return book_file 


if __name__ == '__main__': 
    book = Book()
    date = datetime.utcnow() - timedelta(days=10)
    book_info = book.get_book_info(book_id=1, user_id=2, date_now=date)
    book_file = make_pdf_book(book_info)

    with open(book_file['pdf_file_name'], "w") as f:
        f.write(book_file['pdf_file'])

    print(book_file['pdf_file_name'])
    

