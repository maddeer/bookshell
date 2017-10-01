import docx


def docx_to_text(docx_file):
    f = open(docx_file, 'rb')
    document = docx.Document(f)
    f.close()

    docText = '\n\n'.join([
        paragraph.text for paragraph in document.paragraphs
    ])
    return docText

