from django.conf.urls.defaults import *
import sys
#code promoted to daresdev directory
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^dare/', include('dare.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
