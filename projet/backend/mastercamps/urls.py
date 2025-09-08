"""
URL configuration for mastercamps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from django.shortcuts import render
from api.views import ImageUploadView
import os

def upload_interface(request):
    """Servir l'interface d'upload HTML"""
    interface_path = os.path.join(settings.BASE_DIR, 'upload_interface.html')
    return FileResponse(open(interface_path, 'rb'), content_type='text/html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('upload/', upload_interface, name='upload-interface'),
    # Route directe pour l'upload d'images si le frontend appelle /upload au lieu de /api/upload/
    path('upload', ImageUploadView.as_view(), name='direct-image-upload'),
    # Route pour le frontend qui appelle /api/upload directement
    path('api/upload', ImageUploadView.as_view(), name='frontend-upload'),
]

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
