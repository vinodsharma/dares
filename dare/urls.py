from django.conf.urls.defaults import *

urlpatterns = patterns('dare.views.users',
    (r'^login', 'userLogin'),
    (r'^logout', 'userLogout'),
)

urlpatterns = urlpatterns+patterns('dare.views.daresdata',
    (r'^profile', 'getProfile'),
    (r'^post', 'setPostData'),
    (r'^darestats', 'getDareStats'),
    (r'^mystats', 'getFullProfile'),
)

