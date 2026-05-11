import io
import base64
from PIL import Image

def compress_image(image_file, quality=75):
    """
    Comprime a imagem mantendo o formato original.
    Retorna os bytes da imagem comprimida.
    """
    img = Image.open(image_file)
    original_format = img.format
    output_format = original_format if original_format in ('JPEG', 'PNG', 'WEBP') else 'JPEG'
    
    save_kwargs = {'optimize': True}
    if output_format in ('JPEG', 'WEBP'):
        # qualidade 1-100
        save_kwargs['quality'] = quality
    elif output_format == 'PNG':
        # compress_level 0-9; mapear quality 1-100 para 0-9
        compress_level = int((100 - quality) / 10)  # qualidade alta = nível baixo
        compress_level = max(0, min(9, compress_level))
        save_kwargs['compress_level'] = compress_level
    
    # Converter CMYK para RGB se necessário
    if img.mode == 'CMYK' and output_format != 'PNG':
        img = img.convert('RGB')
    elif img.mode == 'RGBA' and output_format == 'JPEG':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    
    buffer = io.BytesIO()
    img.save(buffer, format=output_format, **save_kwargs)
    buffer.seek(0)
    return buffer.getvalue(), output_format

def get_image_thumbnail(image_bytes, max_width=150):
    """Gera thumbnail em base64 para pré-visualização."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img.thumbnail((max_width, new_height), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except Exception:
        return None