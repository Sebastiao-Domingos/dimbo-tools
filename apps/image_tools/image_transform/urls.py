from django.urls import path
from . import views

app_name = 'image_transform'
urlpatterns = [
    path('rotate-flip/', views.rotate_flip, name='rotate_flip'),
    path('crop/', views.crop, name='crop'),
]