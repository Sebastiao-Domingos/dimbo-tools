from django.urls import path
from . import views

app_name = 'image_editor'
urlpatterns = [
    path('', views.editor, name='editor'),
    path('upload/', views.upload_image, name='upload'),
    path('save/', views.save_image, name='save'),
    path('save-project/', views.save_project, name='save_project'),
    path('matrix-split/', views.matrix_split, name='matrix_split'),
    path('list-projects/', views.list_projects, name='list_projects'),
    path('load-project/<int:project_id>/', views.load_project, name='load_project'),
]