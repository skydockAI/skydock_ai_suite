import os
from docx import Document
import PyPDF2

def read_all_text_from_file(file_path):
    result = ""
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.txt' or file_extension == '.text':
        with open(file_path, 'r', encoding='utf-8') as file:
            result = file.read()
    elif file_extension == '.docx':
        document = Document(file_path)
        result = '\n'.join([para.text for para in document.paragraphs])
    elif file_extension == '.pdf':
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                result += page.extract_text() or ''     
    return result