from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),  # ← linha essencial
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('image/', include('apps.image_tools.converter.urls')),
    path('image/compress/', include('apps.image_tools.compressor.urls')),
    path('image/remove-bg/', include('apps.image_tools.bg_remover.urls')),
    path('image/resize/', include('apps.image_tools.resize.urls')),
    path('image/transform/', include('apps.image_tools.image_transform.urls')),
    path('image/editor/', include('apps.image_tools.editor.urls')),
    path('pdf/', include('apps.toolspdfs.pdf_tools.urls')),
    path('pdf-converter/', include('apps.toolspdfs.pdf_converter.urls')),
    path('pdf-editor/', include('apps.toolspdfs.pdf_pro.urls')),
]