from datetime import datetime
from pdfclass import PDF 
from databaseinit import Users, Autors, Books, Chapters 


def get_book_by_id(book_id):
    date_now = datetime.utcnow()
    book = Books.query.filter(Books.book_id == book_id).first()

    book_chapters = Chapters.query.\
            filter(Chapters.book_id == book.book_id).\
            filter(Chapters.date_to_open < date_now).\
            group_by(Chapters.chapter_number).all()

    autors = Users.query.join(Autors, Autors.user_id == Users.user_id).filter(Autors.book_id == book_id).all()
    book_dict = {'book_data': book, 'autors': autors, 'book_chapters': book_chapters}
    return book_dict


def make_pdf_book(book): 
    pdf = PDF()
    #init_pdf(pdf)
    pdf.add_font('Arial', '', 'LiberationSans-Regular.ttf', uni=True)
    pdf.add_font('Arial-Bold', '', 'LiberationSans-Bold.ttf', uni=True)
    pdf.add_font('Times', '', 'LiberationSerif-Regular.ttf', uni=True)
    pdf.alias_nb_pages()

    pdf.book_name = book['book_data'].book_name
    pdf.set_title(pdf.book_name)

    for autor in book['autors']: 
        pdf.set_author(autor.full_name)

    pdf.title_page(book['autors'], pdf.book_name)
    pdf.add_page()
    pdf.chapter_body(book['book_data'].book_description)

    for chapter in book['book_chapters']:
        pdf.title = chapter.chapter_title
        pdf.print_chapter(pdf.book_name, chapter.chapter_number, chapter.chapter_title, chapter.chapter_text)

    pdf.output('tuto2.pdf', 'F')
    return 'tuto2.pdf'


if __name__ == '__main__': 
    book_file = make_pdf_book(get_book_by_id(1))
    print(book_file)
    

