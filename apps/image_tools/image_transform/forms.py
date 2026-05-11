from django import forms

class RotateFlipForm(forms.Form):
    imagem = forms.ImageField(label='Imagem')
    acao = forms.ChoiceField(
        label='Transformação',
        choices=[
            ('rot90', 'Rotacionar 90° para a direita'),
            ('rot180', 'Rotacionar 180°'),
            ('rot270', 'Rotacionar 90° para a esquerda'),
            ('flip_horizontal', 'Espelhar horizontalmente'),
            ('flip_vertical', 'Espelhar verticalmente'),
        ],
        initial='rot90'
    )

class CropForm(forms.Form):
    imagem = forms.ImageField(label='Imagem')
    left = forms.IntegerField(label='Esquerda (px)', min_value=0, required=True)
    top = forms.IntegerField(label='Topo (px)', min_value=0, required=True)
    right = forms.IntegerField(label='Direita (px)', min_value=0, required=True)
    bottom = forms.IntegerField(label='Baixo (px)', min_value=0, required=True)

    def clean(self):
        cleaned_data = super().clean()
        left = cleaned_data.get('left')
        top = cleaned_data.get('top')
        right = cleaned_data.get('right')
        bottom = cleaned_data.get('bottom')
        if left is not None and right is not None:
            if left >= right:
                raise forms.ValidationError('A coordenada "Direita" deve ser maior que "Esquerda".')
        if top is not None and bottom is not None:
            if top >= bottom:
                raise forms.ValidationError('A coordenada "Baixo" deve ser maior que "Topo".')
        return cleaned_data