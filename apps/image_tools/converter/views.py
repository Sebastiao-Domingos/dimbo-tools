from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .forms import ImageConverterForm
from .services import convert_image
from apps.analytics.models import ConversionLog
from apps.subscriptions.decorators import require_conversion_capability


@login_required
@require_conversion_capability
def converter_view(request):
    if request.method == 'POST':
        form = ImageConverterForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Dados do formulário
                image = form.cleaned_data['image']
                target = form.cleaned_data['target_format']
                quality = form.cleaned_data.get('quality', 85)
                resize = form.cleaned_data.get('resize', False)
                width = form.cleaned_data.get('width')
                height = form.cleaned_data.get('height')
                
                # Conversão da imagem
                converted_data, meta = convert_image(
                    image, target, quality, resize, width, height
                )
                
                # Incrementar contagem de conversões do utilizador
                request.user.increment_conversion()
                
                # Guardar log da conversão
                if request.user.is_authenticated:
                    ConversionLog.objects.create(
                        user=request.user,
                        tool_name='image_converter',
                        original_format=meta['original_format'],
                        target_format=meta['target_format'],
                        original_size=meta['original_size'],
                        converted_size=meta['converted_size'],
                        width=meta['width'],
                        height=meta['height'],
                        quality=meta.get('quality')
                    )
                
                # Preparar resposta para download
                response = HttpResponse(converted_data, content_type=f'image/{target.lower()}')
                response['Content-Disposition'] = f'attachment; filename="converted.{target.lower()}"'
                return response
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        
        return JsonResponse({'error': form.errors}, status=400)
    
    # GET: exibir formulário
    return render(request, 'image_tools/converter.html')