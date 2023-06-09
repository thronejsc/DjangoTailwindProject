"""chronicle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import  TemplateView
# from chronicle import app
from .views import index, journal_list2
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('j2', journal_list2, name='j2'),
    path('profiles/', include('app.urls')),
    path('profiles/', include('django.contrib.auth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include('social_django.urls', namespace='social'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
