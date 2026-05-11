from django import forms

class BgRemoverForm(forms.Form):
    imagem = forms.ImageField(
        label='Imagem',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    # Opcional: manter ou remover a transparência? (rembg já gera PNG com transparência)