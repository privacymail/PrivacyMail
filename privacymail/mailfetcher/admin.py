from django.contrib import admin
from mailfetcher.models import Mail, Eresource, Thirdparty

# Register your models here.
admin.site.register(Mail)
admin.site.register(Eresource)
admin.site.register(Thirdparty)
