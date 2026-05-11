from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from apps.subscriptions.decorators import require_conversion_capability
from .forms import MergePDFForm, SplitPDFForm, ProtectPDFForm, CompressPDFForm
from .services import merge_pdfs, protect_pdf, compress_pdf_advanced,split_pdf_into_parts,get_pdf_thumbnail
from apps.analytics.models import ConversionLog

# @login_required
# @require_conversion_capability
# def merge(request):
#     if request.method == 'POST':
#         form = MergePDFForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 pdf_files = request.FILES.getlist('pdf_files')
#                 if len(pdf_files) < 2:
#                     return JsonResponse({'error': 'Envie pelo menos 2 PDFs para juntar.'}, status=400)
#                 merged_data = merge_pdfs(pdf_files)
#                 # Log
#                 ConversionLog.objects.create(
#                     user=request.user,
#                     tool_name='pdf_merge',
#                     original_format='PDF',
#                     target_format='PDF',
#                     original_size=sum(f.size for f in pdf_files),
#                     converted_size=len(merged_data)
#                 )
#                 request.user.increment_conversion()
#                 response = HttpResponse(merged_data, content_type='application/pdf')
#                 response['Content-Disposition'] = 'attachment; filename="merged.pdf"'
#                 return response
#             except Exception as e:
#                 return JsonResponse({'error': str(e)}, status=400)
#         return JsonResponse({'error': form.errors}, status=400)
#     return render(request, 'pdf_tools/merge.html', {'form': MergePDFForm()})

@login_required
@require_conversion_capability
def merge(request):
    if request.method == 'POST':
        form = MergePDFForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_files = request.FILES.getlist('pdf_files')
                if len(pdf_files) < 2:
                    return JsonResponse({'error': 'Envie pelo menos 2 PDFs para juntar.'}, status=400)
                
                merged_data = merge_pdfs(pdf_files)
                
                request.user.increment_conversion()
                from apps.analytics.models import ConversionLog
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_merge',
                    original_format='PDF',
                    target_format='PDF',
                    original_size=sum(f.size for f in pdf_files),
                    converted_size=len(merged_data),
                )
                
                # Gerar miniatura do PDF resultante
                from .services import get_pdf_thumbnail
                import base64
                thumbnail = get_pdf_thumbnail(merged_data, max_width=150)
                
                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(merged_data).decode('utf-8'),
                    'filename': 'merged.pdf',
                    'thumbnail': thumbnail,
                    'num_files': len(pdf_files),
                    'total_pages': None,  # seria bom extrair, mas opcional
                    'original_size': sum(f.size for f in pdf_files),
                    'converted_size': len(merged_data)
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)
    form = MergePDFForm()
    return render(request, 'pdf_tools/merge.html', {'form': form})


@login_required
@require_conversion_capability
def compress(request):
    if request.method == 'POST':
        form = CompressPDFForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = request.FILES['pdf_file']
                level = form.cleaned_data['compression_level']
                compressed_data = compress_pdf_advanced(pdf_file, level)

                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_compress',
                    original_format='PDF',
                    target_format='PDF',
                    original_size=pdf_file.size,
                    converted_size=len(compressed_data),
                )

                import base64
               
                original_size = pdf_file.size
                compressed_size = len(compressed_data)
                reduction = ((original_size - compressed_size) / original_size) * 100

                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(compressed_data).decode('utf-8'),
                    'filename': f'compressed_{level}.pdf',
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction_percent': round(reduction, 1)
                }

                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Ficheiro inválido', 'details': form.errors}, status=400)
    form = CompressPDFForm()
    return render(request, 'pdf_tools/compress.html', {'form': form})

@login_required
@require_conversion_capability
def protect(request):
    if request.method == 'POST':
        form = ProtectPDFForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = request.FILES['pdf_file']
                password = form.cleaned_data['password']
                protected_data = protect_pdf(pdf_file, password)

                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_protect',
                    original_format='PDF',
                    target_format='PDF',
                    original_size=pdf_file.size,
                    converted_size=len(protected_data),
                )

                import base64

                thumbnail = get_pdf_thumbnail(protected_data, max_width=150)

                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(protected_data).decode('utf-8'),
                    'filename': 'protected.pdf',
                    'thumbnail': thumbnail,
                    'password_used': password 
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Ficheiro ou palavra-passe inválidos', 'details': form.errors}, status=400)
    form = ProtectPDFForm()
    return render(request, 'pdf_tools/protect.html', {'form': form})

# apps/pdf_tools/views.py



@login_required
@require_conversion_capability
def split(request):
    if request.method == 'POST':
        form = SplitPDFForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            groups_str = form.cleaned_data['pages']  # campo 'pages' agora contém grupos separados por ';'
            try:
                parts = split_pdf_into_parts(pdf_file, groups_str)
                if not parts:
                    return JsonResponse({'error': 'Nenhuma página válida foi extraída.'}, status=400)

                # Registar no log (uma única entrada para a operação de split)
                total_original_size = pdf_file.size
                total_converted_size = sum(len(p['data']) for p in parts)
                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_split',
                    original_format='PDF',
                    target_format='PDF',
                    original_size=total_original_size,
                    converted_size=total_converted_size,
                )

                # Prepara resposta JSON (sem enviar os bytes grandes, podemos enviar os PDFs um a um pelo frontend)
                # Em vez de enviar os bytes todos no JSON, enviamos apenas metadados e depois o frontend faz download de cada parte via outra rota?
                # Opto por enviar os bytes codificados em base64 no JSON (cuidado com tamanho).
                # Alternativa: guardar as partes em sessão e depois servir via endpoint.
                # Vou fazer simples: enviar base64 dos PDFs no JSON (para partes pequenas é ok, mas para grandes pode dar problema).
                # Solução mais robusta: guardar em cache (Redis) e devolver IDs.
                # Para simplificar, envio base64.
                import base64
                parts_data = []
                for p in parts:
                    parts_data.append({
                        'name': p['name'],
                        'data': base64.b64encode(p['data']).decode('utf-8'),
                        'thumbnail': p['thumbnail'],
                        'pages': p['pages']
                    })
                return JsonResponse({'success': True, 'parts': parts_data})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)

    form = SplitPDFForm()
    return render(request, 'pdf_tools/split.html', {'form': form})