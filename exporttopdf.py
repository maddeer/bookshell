from datetime import datetime, timedelta

from PyCRC.CRC32 import CRC32

from pdfclass import PDF 
from models import Book
from translit import transliterate 



def make_pdf_book(book): 
    pdf = PDF()
    pdf.add_font('Arial', '', 'LiberationSans-Regular.ttf', uni=True)
    pdf.add_font('Arial-Bold', '', 'LiberationSans-Bold.ttf', uni=True)
    pdf.add_font('Times', '', 'LiberationSerif-Regular.ttf', uni=True)
    pdf.alias_nb_pages()

    pdf.book_name = book['book_data'].book_name
    pdf.set_title(pdf.book_name)

    authors = ''
    for author in book['book_authors']: 
        pdf.set_author('BookShell 0.1')
        authors += author.full_name.replace(' ', '_') + '_'

    pdf.title_page(book['book_authors'], pdf.book_name)
    pdf.add_page()
    pdf.chapter_body(book['book_data'].book_description)

    book_text = ''
    for chapter in book['book_chapters']:
        pdf.title = chapter.chapter_title
        pdf.print_chapter(chapter.chapter_number, chapter.chapter_title, chapter.chapter_text)
        book_text += chapter.chapter_text
    crc32 = CRC32().calculate(book_text)
    pdf_file_name = '{}_{}_{}.pdf'.format(authors, pdf.book_name.replace(' ', '_'), crc32)
    pdf_file_name = transliterate(pdf_file_name)

    pdf.output(pdf_file_name, 'F')
    return pdf_file_name


if __name__ == '__main__': 
    book = Book()
    date = datetime.utcnow() - timedelta(days=10)
    book_info = book.get_book_info(book_id=1, user_id=2, date_now=date)
    print(book_info)
    book_file = make_pdf_book(book_info)
    print(book_file)
    

