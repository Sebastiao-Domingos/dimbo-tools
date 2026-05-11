from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import ImageCompressForm
from .services import compress_image, get_image_thumbnail
import base64

@login_required
@require_conversion_capability
def compress_image_view(request):
    if request.method == 'POST':
        form = ImageCompressForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                image = request.FILES['image']
                quality = form.cleaned_data['quality']
                compressed_data, output_format = compress_image(image, quality)
                
                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='image_compressor',
                    original_format=image.content_type.split('/')[-1].upper(),
                    target_format=output_format,
                    original_size=image.size,
                    converted_size=len(compressed_data),
                )
                
                thumbnail = get_image_thumbnail(compressed_data, max_width=150)
                original_size = image.size
                compressed_size = len(compressed_data)
                reduction = ((original_size - compressed_size) / original_size) * 100
                
                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(compressed_data).decode('utf-8'),
                    'filename': f'compressed.{output_format.lower()}',
                    'thumbnail': thumbnail,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction_percent': round(reduction, 1)
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)
    form = ImageCompressForm()
    return render(request, 'image_tools/compressor.html', {'form': form})