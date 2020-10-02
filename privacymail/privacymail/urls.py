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
from django.urls import path, re_path, include
from django.conf.urls import url
from api.views import *
from identity.views import *

urlpatterns = [
    path('api/', include('api.urls')),
    path('/', FrontendAppView.as_view(), name="FrontendApp"),
    path('', FrontendAppView.as_view(), name="FrontendApp"),
    path('testA/', FrontendAppView.as_view(), name="FrontendApp"),
    path('testB/', StatisticTestView.as_view(), name="StatisticTest"),
    url(r'^$', FrontendAppView.as_view(), name="FrontendApp")
]
