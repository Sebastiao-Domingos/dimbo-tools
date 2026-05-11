from django import forms

class ResizeForm(forms.Form):
    imagem = forms.ImageField(label='Imagem')
    largura = forms.IntegerField(label='Largura (px)', min_value=1, max_value=5000, required=False)
    altura = forms.IntegerField(label='Altura (px)', min_value=1, max_value=5000, required=False)
    manter_proporcao = forms.BooleanField(label='Manter proporção', required=False, initial=True)

    def clean(self):
        cleaned_data = super().clean()
        largura = cleaned_data.get('largura')
        altura = cleaned_data.get('altura')
        if not largura and not altura:
            raise forms.ValidationError('Indique pelo menos a largura ou a altura para redimensionar.')
        return cleaned_data