from django import forms

class ImageUploadForm(forms.Form):
    imagem = forms.ImageField(label='Imagem')