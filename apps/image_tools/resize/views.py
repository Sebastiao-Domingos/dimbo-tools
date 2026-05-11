import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import ResizeForm
from .services import redimensionar_imagem, gerar_thumbnail

@login_required
@require_conversion_capability
def resize_view(request):
    if request.method == 'POST':
        form = ResizeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imagem = request.FILES['imagem']
                largura = form.cleaned_data.get('largura')
                altura = form.cleaned_data.get('altura')
                manter_proporcao = form.cleaned_data.get('manter_proporcao', True)

                imagem_bytes = imagem.read()
                imagem_redimensionada, formato, (nova_l, nova_a) = redimensionar_imagem(
                    imagem_bytes, largura, altura, manter_proporcao
                )

                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='image_resize',
                    original_format=imagem.content_type.split('/')[-1].upper(),
                    target_format=formato,
                    original_size=imagem.size,
                    converted_size=len(imagem_redimensionada),
                )

                thumbnail = gerar_thumbnail(imagem_redimensionada)

                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(imagem_redimensionada).decode('utf-8'),
                    'filename': f'redimensionada.{formato.lower()}',
                    'thumbnail': thumbnail,
                    'original_size': imagem.size,
                    'new_size': len(imagem_redimensionada),
                    'new_dimensions': f'{nova_l}x{nova_a}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)

    form = ResizeForm()
    return render(request, 'image_tools/resize.html', {'form': form})