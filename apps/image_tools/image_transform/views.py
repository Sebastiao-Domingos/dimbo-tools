import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import RotateFlipForm, CropForm
from .services import rotacionar_espelhar, cortar_imagem, gerar_thumbnail

@login_required
@require_conversion_capability
def rotate_flip(request):
    if request.method == 'POST':
        form = RotateFlipForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imagem = request.FILES['imagem']
                acao = form.cleaned_data['acao']
                imagem_bytes = imagem.read()
                imagem_processada, formato = rotacionar_espelhar(imagem_bytes, acao)
                
                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='image_rotate_flip',
                    original_format=imagem.content_type.split('/')[-1].upper(),
                    target_format=formato,
                    original_size=imagem.size,
                    converted_size=len(imagem_processada),
                )
                
                thumbnail = gerar_thumbnail(imagem_processada)
                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(imagem_processada).decode('utf-8'),
                    'filename': f'transformada.{formato.lower()}',
                    'thumbnail': thumbnail,
                    'original_size': imagem.size,
                    'new_size': len(imagem_processada),
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)
    
    form = RotateFlipForm()
    return render(request, 'image_tools/rotate_flip.html', {'form': form})

@login_required
@require_conversion_capability
def crop(request):
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                imagem = request.FILES['imagem']
                left = form.cleaned_data['left']
                top = form.cleaned_data['top']
                right = form.cleaned_data['right']
                bottom = form.cleaned_data['bottom']
                imagem_bytes = imagem.read()
                imagem_cortada, formato, dims = cortar_imagem(imagem_bytes, left, top, right, bottom)
                
                request.user.increment_conversion()
                ConversionLog.objects.create(
                    user=request.user,
                    tool_name='image_crop',
                    original_format=imagem.content_type.split('/')[-1].upper(),
                    target_format=formato,
                    original_size=imagem.size,
                    converted_size=len(imagem_cortada),
                )
                
                thumbnail = gerar_thumbnail(imagem_cortada)
                response_data = {
                    'success': True,
                    'file_data': base64.b64encode(imagem_cortada).decode('utf-8'),
                    'filename': f'cortada.{formato.lower()}',
                    'thumbnail': thumbnail,
                    'original_size': imagem.size,
                    'new_size': len(imagem_cortada),
                    'new_dimensions': f'{dims[0]}x{dims[1]}'
                }
                return JsonResponse(response_data)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        return JsonResponse({'error': 'Formulário inválido', 'details': form.errors}, status=400)
    
    form = CropForm()
    return render(request, 'image_tools/crop.html', {'form': form})