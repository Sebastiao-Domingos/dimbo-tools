import io
import base64
from PIL import Image
from rembg import remove

def remover_fundo(imagem_bytes):
    """Remove o fundo da imagem utilizando o modelo u2net."""
    imagem_sem_fundo = remove(imagem_bytes)  # retorna bytes da imagem PNG (com canal alpha)
    return imagem_sem_fundo

def gerar_thumbnail(imagem_bytes, largura_max=150):
    """Gera uma thumbnail da imagem (primeiro frame) para preview."""
    try:
        img = Image.open(io.BytesIO(imagem_bytes))
        # converte para RGB se for necessário (evita problemas com modo P ou CMYK)
        if img.mode not in ('RGBA', 'RGB'):
            img = img.convert('RGB')
        # redimensiona mantendo proporção
        ratio = largura_max / img.width
        nova_altura = int(img.height * ratio)
        img.thumbnail((largura_max, nova_altura), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except Exception:
        return None