from django.urls import path
from . import views

app_name = 'pdf_tools'

urlpatterns = [
    path('merge/', views.merge, name='merge'),
    path('split/', views.split, name='split'),
    path('protect/', views.protect, name='protect'),
    path('compress/', views.compress, name='compress'),
]