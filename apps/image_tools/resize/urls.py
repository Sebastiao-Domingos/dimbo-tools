from django.urls import path
from . import views

app_name = 'image_resize'
urlpatterns = [
    path('', views.resize_view, name='resize'),
]