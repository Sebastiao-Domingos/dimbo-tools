import io
from PIL import Image
from django.core.exceptions import ValidationError

SUPPORTED_INPUT = ['PNG', 'JPEG', 'JPG', 'WEBP', 'BMP', 'GIF']
SUPPORTED_OUTPUT = ['PNG', 'JPEG', 'WEBP', 'BMP', 'GIF']

def convert_image(image_file, target_format, quality=85, resize=False, width=None, height=None):
    """
    Converte imagem e retorna (bytes, metadata)
    """
    target = target_format.upper()
    if target == 'JPG':
        target = 'JPEG'
    if target not in SUPPORTED_OUTPUT:
        raise ValidationError(f'Formato {target} não suportado')
    
    img = Image.open(image_file)
    original_format = img.format or 'UNKNOWN'
    original_size = image_file.size
    
    # Tratamento de transparência para JPEG
    if target == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode == 'CMYK':
        img = img.convert('RGB')
    
    # Redimensionamento proporcional
    if resize and (width or height):
        original_w, original_h = img.size
        if width and not height:
            ratio = width / original_w
            height = int(original_h * ratio)
        elif height and not width:
            ratio = height / original_h
            width = int(original_w * ratio)
        if width and height:
            img.thumbnail((width, height), Image.LANCZOS)
    
    buffer = io.BytesIO()
    save_kwargs = {}
    if target in ('JPEG', 'WEBP'):
        save_kwargs['quality'] = quality
        save_kwargs['optimize'] = True
    elif target == 'PNG':
        save_kwargs['compress_level'] = 6
    
    img.save(buffer, format=target, **save_kwargs)
    buffer.seek(0)
    
    converted_size = buffer.getbuffer().nbytes
    metadata = {
        'original_format': original_format,
        'target_format': target,
        'original_size': original_size,
        'converted_size': converted_size,
        'width': img.width,
        'height': img.height,
        'quality': quality if target in ('JPEG', 'WEBP') else None,
        'resized': resize
    }
    return buffer.getvalue(), metadata