from django.urls import path
from . import views

app_name = 'pdf_pro'

urlpatterns = [
    path('', views.pdf_editor, name='editor_home'),
    path('<uuid:pdf_id>/', views.pdf_editor, name='editor_detail'),
    path('api/pdf/<uuid:pdf_id>/update/', views.api_update_pdf, name='api_update'),
]