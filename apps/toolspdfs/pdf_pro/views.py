from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import PDFDocument, PDFOperation
from .utils import process_pdf_reorder
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PDFDocument
import fitz  # PyMuPDF

@login_required
def pdf_editor(request, pdf_id=None):
    pdf = None
    pages_data = []

    if pdf_id:
        pdf = get_object_or_404(PDFDocument, id=pdf_id, user=request.user)
        # Abrir o PDF para gerar miniaturas ou dados das páginas
        doc = fitz.open(pdf.original_file.path)
        for i in range(len(doc)):
            pages_data.append({'index': i, 'number': i + 1})
        doc.close()

    if request.method == 'POST' and not pdf_id:
        # Lógica de Upload Inicial
        uploaded_file = request.FILES.get('pdf_file')
        if uploaded_file:
            # Validar se é PDF
            if not uploaded_file.name.endswith('.pdf'):
                return render(request, 'editor_pdf.html', {'error': 'Por favor, envie um ficheiro PDF válido.'})
            
            new_pdf = PDFDocument.objects.create(
                user=request.user,
                original_file=uploaded_file,
                name=uploaded_file.name,
                size=uploaded_file.size
            )
            # Abrir para contar páginas
            doc = fitz.open(new_pdf.original_file.path)
            new_pdf.page_count = len(doc)
            new_pdf.save()
            doc.close()
            
            return redirect('pdf_pro:editor_detail', pdf_id=new_pdf.id)

    return render(request, 'editor_pdf.html', {
        'pdf': pdf,
        'pages': pages_data
    })

def api_update_pdf(request, pdf_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        operation_type = data.get('type')
        
        pdf = get_object_or_404(PDFDocument, id=pdf_id, user=request.user)
        
        if operation_type == 'REORDER':
            new_order = data.get('pages') # ex: [0, 1, 4, 5]
            try:
                process_pdf_reorder(pdf.id, new_order)
                return JsonResponse({'status': 'success', 'message': 'PDF atualizado!'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
                
    return JsonResponse({'status': 'invalid_request'}, status=400)