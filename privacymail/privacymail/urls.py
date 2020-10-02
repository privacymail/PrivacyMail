"""privacymail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.views.generic import TemplateView
from django.urls import path, re_path, include
from api.views import *
from identity.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('favicon.ico', TemplateView.as_view(template_name='favicon.ico'), name="favicon"),
    path('logo192.png', TemplateView.as_view(template_name='logo192.png'), name="logo192"),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json'), name="manifest"),
    re_path(r'^', TemplateView.as_view(template_name='index.html'), name="ReactApp"),
]
