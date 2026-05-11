from django.apps import AppConfig

class TransformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.image_tools.image_transform'
    verbose_name = 'Transformações de Imagem'