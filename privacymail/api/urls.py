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
from django.urls import path
from . import views
from identity.views import *
from mailfetcher.views import *


urlpatterns = [
    path('service/<int:service>/', ServiceView.as_view(), name='Service'),
    path('service/', ServiceView.as_view(), name='ServiceLookup'),
    path('services/', ServiceListView.as_view(), name="ServiceList"),
    path('embed/<int:embed>/', EmbedView.as_view(), name='Embed'),
    path('embed/', EmbedView.as_view(), name='EmbedLookup'),
    path('identity/', IdentityView.as_view(), name='IdentityCreation'),
    path('statistics', StatisticView.as_view(), name='Statistic'),
    path('bookmarklet/identity/', views.BookmarkletApiView.as_view(), name="BookmarkletApiEndpoint")
]
