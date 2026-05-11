from django.db import models
from django.conf import settings

class ImageProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Novo Projeto")
    # Este campo guarda o JSON do Fabric.js (camadas, textos, posições)
    canvas_json = models.JSONField() 
    # Miniatura para a galeria
    preview = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"