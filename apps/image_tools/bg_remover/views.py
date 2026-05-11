import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import BgRemoverForm
from .services import remover_fundo, gerar_thumbnail

@login_required
@require_conversion_capability
def bg_remover(request):
    if request.method == 'POST':
        form = BgRemoverForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imagem_original = request.FILES['imagem']
                imagem_bytes = imagem_original.read()

                # processa a imagem (remove o fundo)
                imagem_processada_bytes = remover_fundo(imagem_bytes)

                # registo da conversão
                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='bg_remover',
                    original_format=imagem_original.content_type.split('/')[-1].upper(),
                    target_format='PNG',
                    original_size=imagem_original.size,
                    converted_size=len(imagem_processada_bytes),
                )

                # gera thumbnail da imagem processada
                thumbnail = gerar_thumbnail(imagem_processada_bytes)

                # prepara resposta
                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(imagem_processada_bytes).decode('utf-8'),
                    'filename': 'sem_fundo.png',
                    'thumbnail': thumbnail,
                    'original_size': imagem_original.size,
                    'processed_size': len(imagem_processada_bytes),
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)

    form = BgRemoverForm()
    return render(request, 'image_tools/bg_remover.html', {'form': form})