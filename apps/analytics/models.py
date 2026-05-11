from django.db import models
from django.conf import settings

class ConversionLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversions')
    tool_name = models.CharField(max_length=100, default='image_converter')
    original_format = models.CharField(max_length=10)
    target_format = models.CharField(max_length=10)
    original_size = models.PositiveIntegerField()
    converted_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    quality = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Registo de conversão'
        verbose_name_plural = 'Registos de conversões'

    def __str__(self):
        return f"{self.user.username} - {self.original_format} → {self.target_format} em {self.created_at.strftime('%d/%m/%Y %H:%M')}"