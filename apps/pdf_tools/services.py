# apps/pdf_tools/services.py

import io
import base64
from PyPDF2 import PdfReader, PdfWriter
import pymupdf  # PyMuPDF
import shutil
import subprocess
import tempfile
import os


def merge_pdfs(pdf_files):
    """Junta múltiplos PDFs num só."""
    writer = PdfWriter()
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            writer.add_page(page)
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()


def protect_pdf(pdf_file, password):
    """
    Adiciona palavra-passe ao PDF.
    """
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def split_pdf_into_parts(pdf_file, groups_str):
    """
    Divide um PDF em várias partes conforme os grupos especificados.
    groups_str: string como "1-3;5;7-9"
    Retorna lista de dicionários: [{'name': 'parte_1.pdf', 'data': bytes, 'thumbnail': str_base64, 'pages': [0,1,2]}, ...]
    """
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    groups = [g.strip() for g in groups_str.split(';') if g.strip()]
    parts = []

    # Para gerar thumbnails, abrir o documento com PyMuPDF
    import tempfile
    # Guardar o conteúdo do ficheiro para reutilização
    pdf_file.seek(0)
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)

    for idx, group in enumerate(groups, start=1):
        writer = PdfWriter()
        selected_pages = set()
        if '-' in group:
            start, end = group.split('-')
            start = int(start) - 1
            end = int(end)
            for p in range(start, min(end, total_pages)):
                selected_pages.add(p)
        else:
            p = int(group) - 1
            if 0 <= p < total_pages:
                selected_pages.add(p)
        if not selected_pages:
            continue

        for page_num in sorted(selected_pages):
            writer.add_page(reader.pages[page_num])

        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        pdf_part_bytes = output.getvalue()

        # Gerar thumbnail (primeira página da parte)
        thumb_base64 = None
        try:
            # pymupdf precisa de um stream ou ficheiro temporário
            part_doc = pymupdf.open(stream=pdf_part_bytes, filetype="pdf")
            if part_doc.page_count > 0:
                page = part_doc[0]
                pix = page.get_pixmap(matrix=pymupdf.Matrix(0.2, 0.2))  # escala 20%
                thumb_bytes = pix.tobytes("png")
                thumb_base64 = base64.b64encode(thumb_bytes).decode('utf-8')
            part_doc.close()
        except Exception:
            thumb_base64 = None

        parts.append({
            'name': f'parte_{idx}.pdf',
            'data': pdf_part_bytes,
            'thumbnail': f"data:image/png;base64,{thumb_base64}" if thumb_base64 else None,
            'pages': list(selected_pages)
        })

    return parts



def compress_pdf_advanced(pdf_file, compression_level='medium'):
    """
    Comprime o PDF com diferentes níveis.
    compression_level: 'low', 'medium', 'high'
    """
    # Se ghostscript estiver disponível, usar (melhor compressão)
    if shutil.which('gs'):
        return _compress_with_ghostscript(pdf_file, compression_level)
    else:
        return _compress_with_pymupdf(pdf_file, compression_level)

def _compress_with_ghostscript(pdf_file, level):
    """Usa Ghostscript para compressão profissional."""
    quality_map = {
        'low': 'ebook',      # ~150 dpi
        'medium': 'printer', # ~300 dpi, boa qualidade
        'high': 'prepress'   # mantém qualidade
    }
    quality = quality_map.get(level, 'ebook')
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_input:
        tmp_input.write(pdf_file.read())
        input_path = tmp_input.name
    output_path = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False).name
    
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS=/{quality}', '-dNOPAUSE', '-dQUIET', '-dBATCH',
        f'-sOutputFile={output_path}', input_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    
    with open(output_path, 'rb') as f:
        compressed_data = f.read()
    
    os.unlink(input_path)
    os.unlink(output_path)
    return compressed_data

def _compress_with_pymupdf(pdf_file, level):
    """Compressão nativa com PyMuPDF (sem Ghostscript)."""
    # Parâmetros consoante nível
    if level == 'low':
        zoom = 0.76   # ~110 dpi
        jpeg_quality = 50
    elif level == 'medium':
        zoom = 1.0    # 150 dpi
        jpeg_quality = 75
    else:  # high
        zoom = 1.5    # 300 dpi (mantém qualidade)
        jpeg_quality = 90
    
    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    new_doc = pymupdf.open()
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Converter página para imagem (com zoom) e depois recriar página como imagem
        # Isso perde texto editável, mas reduz drasticamente o tamanho.
        # Alternativa: manter texto e comprimir imagens.
        # Vamos optar por manter como imagem apenas para compressão máxima:
        if level in ('low', 'medium'):
            # Conversão para imagem (perde texto)
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_data = pix.tobytes("jpeg", jpeg_quality)
            img = pymupdf.Pixmap(pymupdf.csRGB, img_data)
            # Criar nova página com a imagem
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(page.rect, pixmap=img)
        else:
            # Para high, manter texto e apenas comprimir imagens
            # (não implementado aqui para simplificar)
            new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page_num)
    
    output = io.BytesIO()
    new_doc.save(output, garbage=4, deflate=True, clean=True)
    new_doc.close()
    doc.close()
    output.seek(0)
    return output.getvalue()



def get_pdf_thumbnail(pdf_bytes: bytes, max_width=150) -> str:
    """
    Gera uma miniatura (primeira página) de um PDF em base64 (formato PNG).
    """
    try:
        import pymupdf
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        if doc.page_count > 0:
            page = doc[0]
            # calcular zoom para largura máxima desejada (em pontos)
            zoom = max_width / page.rect.width
            mat = pymupdf.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img_data = pix.tobytes("png")
            doc.close()
            return f"data:image/png;base64,{base64.b64encode(img_data).decode('utf-8')}"
        doc.close()
    except Exception:
        pass
    return None