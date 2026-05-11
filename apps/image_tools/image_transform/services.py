import io
import base64
from PIL import Image

def rotacionar_espelhar(imagem_bytes, acao):
    img = Image.open(io.BytesIO(imagem_bytes))
    formato_original = img.format
    
    if acao == 'rot90':
        img = img.rotate(-90, expand=True)   # rotação horária
    elif acao == 'rot180':
        img = img.rotate(180, expand=True)
    elif acao == 'rot270':
        img = img.rotate(90, expand=True)    # rotação anti‑horária
    elif acao == 'flip_horizontal':
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    elif acao == 'flip_vertical':
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    else:
        raise ValueError('Ação inválida')
    
    # converter para RGB se for JPEG e tiver transparência
    if formato_original == 'JPEG' and img.mode == 'RGBA':
        img = img.convert('RGB')
    elif formato_original == 'PNG' and img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    buffer = io.BytesIO()
    img.save(buffer, format=formato_original, optimize=True)
    buffer.seek(0)
    return buffer.getvalue(), formato_original

def cortar_imagem(imagem_bytes, left, top, right, bottom):
    img = Image.open(io.BytesIO(imagem_bytes))
    formato_original = img.format
    # converter coordenadas para inteiros
    left = int(left); top = int(top); right = int(right); bottom = int(bottom)
    if left < 0 or top < 0 or right > img.width or bottom > img.height:
        raise ValueError('Coordenadas fora dos limites da imagem')
    img_cropped = img.crop((left, top, right, bottom))
    
    if formato_original == 'JPEG' and img_cropped.mode == 'RGBA':
        img_cropped = img_cropped.convert('RGB')
    elif formato_original == 'PNG' and img_cropped.mode != 'RGBA':
        img_cropped = img_cropped.convert('RGBA')
    
    buffer = io.BytesIO()
    img_cropped.save(buffer, format=formato_original, optimize=True)
    buffer.seek(0)
    return buffer.getvalue(), formato_original, (img_cropped.width, img_cropped.height)

def gerar_thumbnail(imagem_bytes, largura_max=150):
    try:
        img = Image.open(io.BytesIO(imagem_bytes))
        ratio = largura_max / img.width
        nova_altura = int(img.height * ratio)
        img.thumbnail((largura_max, nova_altura), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except Exception:
        return None