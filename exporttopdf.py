from pdfclass import PDF 
from models import Book


def make_pdf_book(book): 
    pdf = PDF()
    pdf.add_font('Arial', '', 'LiberationSans-Regular.ttf', uni=True)
    pdf.add_font('Arial-Bold', '', 'LiberationSans-Bold.ttf', uni=True)
    pdf.add_font('Times', '', 'LiberationSerif-Regular.ttf', uni=True)
    pdf.alias_nb_pages()

    pdf.book_name = book['book_data'].book_name
    pdf.set_title(pdf.book_name)

    for autor in book['book_autors']: 
        pdf.set_author(autor.full_name)

    pdf.title_page(book['book_autors'], pdf.book_name)
    pdf.add_page()
    pdf.chapter_body(book['book_data'].book_description)

    for chapter in book['book_chapters']:
        pdf.title = chapter.chapter_title
        pdf.print_chapter(chapter.chapter_number, chapter.chapter_title, chapter.chapter_text)

    pdf.output('tuto2.pdf', 'F')
    return 'tuto2.pdf'


if __name__ == '__main__': 
    book = Book()
    book_file = make_pdf_book(book.get_book_info(book_id=1, user_id=1))
    print(book_file)
    

