from django import forms

class MergePDFForm(forms.Form):
    pdf_files = forms.FileField(
        label='Ficheiros PDF',
        required=True,
        help_text='Seleccione dois ou mais PDFs para juntar.'
    )
    # Não definir widget aqui

class SplitPDFForm(forms.Form):
    pdf_file = forms.FileField(label='Ficheiro PDF', required=True)
    pages = forms.CharField(
        label='Páginas a extrair',
        help_text='Exemplo: 1-3,5 (extrai páginas 1 a 3 e a página 5)'
    )

class ProtectPDFForm(forms.Form):
    pdf_file = forms.FileField(label='Ficheiro PDF', required=True)
    password = forms.CharField(
        label='Palavra-passe',
        widget=forms.PasswordInput(render_value=True),
        min_length=4
    )


# apps/pdf_tools/forms.py (adicionar campo)

class CompressPDFForm(forms.Form):
    pdf_file = forms.FileField(label='Ficheiro PDF', required=True)
    compression_level = forms.ChoiceField(
        label='Nível de compressão',
        choices=[
            ('low', 'Baixo (pequeno, perde qualidade)'),
            ('medium', 'Médio (recomendado)'),
            ('high', 'Alto (mantém qualidade)')
        ],
        initial='medium',
        required=True
    )