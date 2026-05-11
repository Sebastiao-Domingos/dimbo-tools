import io
import zipfile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
import pymupdf  # PyMuPDF
from pdf2docx import Converter
from PIL import Image

class PDFConverterService:
    """Serviço centralizado para conversão de PDFs."""

    @staticmethod
    def convert_to_images(pdf_file: InMemoryUploadedFile, image_format: str, quality: int, dpi: int):
        """
        Converte todas as páginas de um PDF para imagens.
        Retorna um dicionário com o nome do ficheiro ZIP e os bytes.
        """
        try:
            pdf_bytes = pdf_file.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            zoom = dpi / 72
            matrix = pymupdf.Matrix(zoom, zoom)
            images = []

            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=matrix)
                img_data = pix.tobytes(output=image_format)
                img = Image.open(io.BytesIO(img_data))

                output_buffer = io.BytesIO()
                save_kwargs = {}
                if image_format in ('jpeg', 'webp'):
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True

                img.save(output_buffer, format=image_format.upper(), **save_kwargs)
                images.append((f'page_{page_num + 1}.{image_format}', output_buffer.getvalue()))

            doc.close()

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for img_name, img_bytes in images:
                    zip_file.writestr(img_name, img_bytes)

            zip_buffer.seek(0)
            return {
                'filename': f'pdf_images.zip',
                'bytes': zip_buffer.getvalue(),
                'num_pages': len(images)
            }

        except Exception as e:
            raise ValidationError(f'Erro ao processar o PDF: {str(e)}')

    @staticmethod
    def convert_to_word(pdf_file: InMemoryUploadedFile):
        """
        Converte um PDF para DOCX.
        Retorna um dicionário com os bytes e o nome do ficheiro.
        """
        try:
            # pdf2docx trabalha com paths, por isso vamos guardar o ficheiro temporariamente
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                for chunk in pdf_file.chunks():
                    tmp_pdf.write(chunk)
                tmp_pdf_path = tmp_pdf.name

            output_docx_path = tempfile.NamedTemporaryFile(suffix='.docx', delete=False).name

            cv = Converter(tmp_pdf_path)
            cv.convert(output_docx_path, start=0, end=None)
            cv.close()

            with open(output_docx_path, 'rb') as f:
                docx_bytes = f.read()

            # Limpeza dos ficheiros temporários
            os.unlink(tmp_pdf_path)
            os.unlink(output_docx_path)

            return {
                'filename': 'converted.docx',
                'bytes': docx_bytes
            }

        except Exception as e:
            raise ValidationError(f'Erro ao converter PDF para Word. PDF pode estar protegido ou ter formato complexo. Detalhes: {str(e)}')