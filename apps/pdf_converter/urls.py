from django.urls import path
from . import views

app_name = 'pdf_converter'

urlpatterns = [
    path('to-image/', views.pdf_to_image, name='to_image'),
    path('to-word/', views.pdf_to_word, name='to_word'),
]