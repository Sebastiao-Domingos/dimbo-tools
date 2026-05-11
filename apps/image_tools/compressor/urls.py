from django.urls import path
from . import views

app_name = 'image_compressor'
urlpatterns = [
    path('', views.compress_image_view, name='compress'),
]