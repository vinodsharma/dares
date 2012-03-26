from django.conf.urls.defaults import *

urlpatterns = patterns('dare.views.users',
    (r'^login', 'userLogin'),
)
