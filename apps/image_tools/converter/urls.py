from django.urls import path
from . import views

app_name = 'image_converter'
urlpatterns = [
    path('converter/', views.converter_view, name='converter'),
]