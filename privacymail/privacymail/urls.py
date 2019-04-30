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
from identity.views import *
from mailfetcher.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('service/<int:service>/', ServiceView.as_view(), name='Service'),
    path('service/<int:service>/set_meta/', ServiceMetaView.as_view(), name='ServiceMeta'),
    re_path('service/.+', ServiceView.as_view(), name='Service'),
    path('mail/<int:mail>/', mailview, name='Mail'),
    path('service/', ServiceView.as_view(), name='ServiceLookup'),
    path('services/', ServiceListView.as_view(), name="ServiceList"),
    path('embed/<int:embed>/', EmbedView.as_view(), name='Embed'),
    path('embed/<int:embed>/set_meta/', EmbedMetaView.as_view(), name='EmbedMeta'),
    path('identity/', IdentityView.as_view(), name='IdentityCreation'),
    path('', HomeView.as_view(), name='Home'),
    path('faq/', FaqView.as_view(), name="FAQ"),
    path('imprint/', ImprintView.as_view(), name="Imprint"),
    path('privacy/', PrivacyPolicyView.as_view(), name="PrivacyPolicy"),
    path('api/', include('api.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
