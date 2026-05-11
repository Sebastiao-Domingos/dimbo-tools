from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import PDFToImageForm, PDFToWordForm
from .services import PDFConverterService

@login_required
@require_conversion_capability
def pdf_to_image(request):
    if request.method == 'POST':
        form = PDFToImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = form.cleaned_data['pdf_file']
                image_format = form.cleaned_data['image_format']
                quality = form.cleaned_data['quality']
                dpi = form.cleaned_data['dpi']

                result = PDFConverterService.convert_to_images(pdf_file, image_format, quality, dpi)

                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_to_image',
                    original_format='PDF',
                    target_format=image_format,
                    original_size=pdf_file.size,
                    converted_size=len(result['bytes']),
                )

                response = HttpResponse(result['bytes'], content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                return response

            except ValidationError as e:
                return JsonResponse({'error': e.message}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Formulário inválido. Verifique os dados enviados.', 'details': form.errors}, status=400)

    form = PDFToImageForm()
    return render(request, 'pdf_converter/to_image.html', {'form': form})

@login_required
@require_conversion_capability
def pdf_to_word(request):
    if request.method == 'POST':
        form = PDFToWordForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pdf_file = form.cleaned_data['pdf_file']
                result = PDFConverterService.convert_to_word(pdf_file)

                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='pdf_to_word',
                    original_format='PDF',
                    target_format='DOCX',
                    original_size=pdf_file.size,
                    converted_size=len(result['bytes']),
                )

                response = HttpResponse(result['bytes'], content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{result["filename"]}"'
                return response

            except ValidationError as e:
                return JsonResponse({'error': e.message}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Formulário inválido. Verifique o ficheiro enviado.', 'details': form.errors}, status=400)

    form = PDFToWordForm()
    return render(request, 'pdf_converter/to_word.html', {'form': form})