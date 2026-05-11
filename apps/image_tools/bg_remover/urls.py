from django.urls import path
from . import views

app_name = 'bg_remover'
urlpatterns = [
    path('', views.bg_remover, name='remover'),
]