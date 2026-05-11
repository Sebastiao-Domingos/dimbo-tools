from django.db import models
from django.conf import settings
import uuid
import os

class PDFDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdfs')
    original_file = models.FileField(upload_to='pdfs/originals/%Y/%m/')
    edited_file = models.FileField(upload_to='pdfs/edited/%Y/%m/', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    page_count = models.IntegerField(default=0)
    size = models.BigIntegerField(default=0) # em bytes
    
    is_protected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Documento PDF"
        ordering = ['-created_at']

class PDFOperation(models.Model):
    TYPES = (
        ('MERGE', 'Fusão'),
        ('SPLIT', 'Divisão'),
        ('WATERMARK', 'Marca de Água'),
        ('PROTECT', 'Proteção'),
        ('REORDER', 'Reordenar'),
    )
    pdf = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='operations')
    type = models.CharField(max_length=20, choices=TYPES)
    parameters = models.JSONField(default=dict) # Guarda a ordem das páginas, texto da marca d'água, etc.
    status = models.CharField(max_length=20, default='PENDING') # PENDING, COMPLETED, FAILED
    timestamp = models.DateTimeField(auto_now_add=True)