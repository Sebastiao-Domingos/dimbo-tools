import io
import base64
from PIL import Image

def redimensionar_imagem(imagem_bytes, largura=None, altura=None, manter_proporcao=True):
    img = Image.open(io.BytesIO(imagem_bytes))
    formato_original = img.format
    largura_original, altura_original = img.size

    if manter_proporcao:
        if largura and altura:
            # se ambos fornecidos, mantém a proporção original e ajusta dentro da caixa
            ratio = min(largura / largura_original, altura / altura_original)
            nova_largura = int(largura_original * ratio)
            nova_altura = int(altura_original * ratio)
        elif largura:
            ratio = largura / largura_original
            nova_largura = largura
            nova_altura = int(altura_original * ratio)
        elif altura:
            ratio = altura / altura_original
            nova_largura = int(largura_original * ratio)
            nova_altura = altura
        else:
            nova_largura, nova_altura = largura_original, altura_original
    else:
        nova_largura = largura or largura_original
        nova_altura = altura or altura_original

    img_resized = img.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)

    # preservar formato original, mas se for JPEG e modo RGBA, converter para RGB
    if formato_original == 'JPEG' and img_resized.mode == 'RGBA':
        img_resized = img_resized.convert('RGB')
    elif formato_original == 'PNG' and img_resized.mode != 'RGBA':
        img_resized = img_resized.convert('RGBA')

    buffer = io.BytesIO()
    img_resized.save(buffer, format=formato_original, optimize=True)
    buffer.seek(0)
    return buffer.getvalue(), formato_original, (nova_largura, nova_altura)

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