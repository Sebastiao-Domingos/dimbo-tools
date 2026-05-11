from django import forms

class ImageConverterForm(forms.Form):
    image = forms.ImageField()
    target_format = forms.ChoiceField(choices=[
        ('PNG', 'PNG'), ('JPEG', 'JPEG'), ('WEBP', 'WEBP'), ('BMP', 'BMP'), ('GIF', 'GIF')
    ])
    quality = forms.IntegerField(min_value=1, max_value=100, required=False, initial=85)
    resize = forms.BooleanField(required=False)
    width = forms.IntegerField(min_value=1, required=False)
    height = forms.IntegerField(min_value=1, required=False)
    
    def clean(self):
        data = super().clean()
        if data.get('resize') and not (data.get('width') or data.get('height')):
            raise forms.ValidationError('Informe largura ou altura para redimensionar')
        return data