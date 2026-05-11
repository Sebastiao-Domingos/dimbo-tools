from django import forms

class ImageCompressForm(forms.Form):
    image = forms.ImageField(label='Imagem')
    quality = forms.IntegerField(
        label='Qualidade / Nível de compressão',
        min_value=1,
        max_value=100,
        initial=75,
        help_text='Para JPEG/WEBP: qualidade (1-100). Para PNG: nível de compressão (1-100 → 0-9).'
    )