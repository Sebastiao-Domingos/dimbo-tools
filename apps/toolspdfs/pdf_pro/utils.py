import fitz  # PyMuPDF
from .models import PDFDocument, PDFOperation
import os


def process_pdf_reorder(pdf_id, new_page_order):
    """
    new_page_order: lista de inteiros [0, 2, 1...] baseado no índice original
    """
    doc_record = PDFDocument.objects.get(id=pdf_id)
    src_path = doc_record.original_file.path
    
    doc = fitz.open(src_path)
    doc.select(new_page_order) # Reordena ou remove páginas
    
    # Salva em um novo buffer
    output_path = src_path.replace('originals', 'edited')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc.save(output_path)
    doc.close()
    
    # Atualiza o record
    doc_record.edited_file.name = output_path.split('media/')[-1]
    doc_record.save()
    return output_path