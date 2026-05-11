import io
import base64
import zipfile
from PIL import Image
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.subscriptions.decorators import require_conversion_capability
from apps.analytics.models import ConversionLog
from .forms import ImageUploadForm
from .models import ImageProject

@login_required
@require_conversion_capability
def editor(request):
    # Apenas renderiza o template
    return render(request, 'image_tools/editor.html')

@login_required
@require_conversion_capability
def upload_image(request):
    """Recebe a imagem carregada e devolve os bytes em base64 para o canvas."""
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            imagem = request.FILES['imagem']
            imagem_bytes = imagem.read()
            base64_data = base64.b64encode(imagem_bytes).decode('utf-8')
            # Descobrir o tipo de conteúdo
            content_type = imagem.content_type
            return JsonResponse({
                'success': True,
                'data': base64_data,
                'content_type': content_type,
                'filename': imagem.name
            })
        return JsonResponse({'error': 'Formulário inválido'}, status=400)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
@require_conversion_capability
def save_image(request):
    """Recebe a imagem editada (base64) e retorna o ficheiro para download."""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        image_data = data.get('image_data')
        filename = data.get('filename', 'editada.png')
        if not image_data:
            return JsonResponse({'error': 'Dados da imagem não fornecidos'}, status=400)
        # remover cabeçalho data:image/png;base64,
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        img_bytes = base64.b64decode(image_data)
        # registar conversão
        request.user.increment_conversion()
        ConversionLog.objects.create(
            user=request.user,
            tool_name='image_editor',
            original_format='PNG',
            target_format='PNG',
            original_size=len(img_bytes),
            converted_size=len(img_bytes),
        )
        response = JsonResponse({'success': True, 'file_data': image_data, 'filename': filename})
        return response
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
@require_conversion_capability
def matrix_split(request):
    """Divide a imagem em N x M partes e devolve um ZIP."""
    if request.method == 'POST':
        imagem = request.FILES.get('imagem')
        rows = int(request.POST.get('rows', 2))
        cols = int(request.POST.get('cols', 2))
        if not imagem:
            return JsonResponse({'error': 'Imagem não enviada'}, status=400)
        if rows < 1 or cols < 1 or rows > 10 or cols > 10:
            return JsonResponse({'error': 'Número de linhas/colunas inválido (1 a 10)'}, status=400)
        
        img = Image.open(imagem)
        width, height = img.size
        tile_w = width // cols
        tile_h = height // rows
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(rows):
                for j in range(cols):
                    left = j * tile_w
                    top = i * tile_h
                    right = left + tile_w
                    bottom = top + tile_h
                    tile = img.crop((left, top, right, bottom))
                    tile_bytes = io.BytesIO()
                    tile.save(tile_bytes, format='PNG')
                    zip_file.writestr(f'tile_{i+1}_{j+1}.png', tile_bytes.getvalue())
        zip_buffer.seek(0)
        zip_data = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
        request.user.increment_conversion()
        ConversionLog.objects.create(
            user=request.user,
            tool_name='image_matrix_split',
            original_format=imagem.content_type.split('/')[-1].upper(),
            target_format='ZIP',
            original_size=imagem.size,
            converted_size=len(zip_buffer.getvalue()),
        )
        return JsonResponse({'success': True, 'file_data': zip_data, 'filename': 'matrix_tiles.zip'})
    return JsonResponse({'error': 'Método não permitido'}, status=405)



@login_required
def save_project(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        
        project_id = data.get('project_id')
        canvas_data = data.get('canvas_json') # JSON vindo do canvas.toJSON()
        preview_data = data.get('preview')     # Pequeno base64 para a miniatura
        
        if project_id:
            project = ImageProject.objects.get(id=project_id, user=request.user)
            project.canvas_json = canvas_data
            project.preview = preview_data
            project.save()
        else:
            project = ImageProject.objects.create(
                user=request.user,
                canvas_json=canvas_data,
                preview=preview_data,
                name=data.get('name', 'Projeto Sem Nome')
            )
            
        return JsonResponse({'success': True, 'project_id': project.id})


@login_required
def list_projects(request):
    """Retorna uma lista de projetos salvos do usuário para o modal."""
    projects = ImageProject.objects.filter(user=request.user).order_by('-updated_at')
    data = [
        {
            'id': p.id,
            'name': p.name,
            'preview': p.preview,
            'updated_at': p.updated_at.strftime("%d/%m/%Y %H:%M")
        } for p in projects
    ]
    return JsonResponse({'success': True, 'projects': data})

@login_required
def load_project(request, project_id):
    """Retorna os dados JSON do projeto para serem carregados no canvas."""
    try:
        project = ImageProject.objects.get(id=project_id, user=request.user)
        return JsonResponse({
            'success': True,
            'canvas_json': project.canvas_json,  # O campo JSONField
            'project_id': project.id,
            'name': project.name
        })
    except ImageProject.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Projeto não encontrado.'}, status=404)