from django import forms

class PDFToImageForm(forms.Form):
    pdf_file = forms.FileField(label='Documento PDF')
    image_format = forms.ChoiceField(
        label='Formato de Imagem',
        choices=[
            ('png', 'PNG'),
            ('jpeg', 'JPEG'),
            ('webp', 'WEBP'),
        ],
        initial='png'
    )
    quality = forms.IntegerField(
        label='Qualidade (1-100)',
        min_value=1,
        max_value=100,
        initial=90,
        help_text='Apenas para JPEG e WEBP'
    )
    dpi = forms.IntegerField(
        label='Resolução (DPI)',
        min_value=72,
        max_value=600,
        initial=150,
        help_text='Quanto maior, melhor a qualidade e maior o ficheiro'
    )

class PDFToWordForm(forms.Form):
    pdf_file = forms.FileField(label='Documento PDF')