import PyPDF2

def extract_text_from_pdf(filepath):
    reader = PyPDF2.PdfReader(filepath)
    full_text = "\n".join([page.extract_text() or '' for page in reader.pages])
    return full_text