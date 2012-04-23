from django.conf.urls.defaults import *

urlpatterns = patterns('dare.views.users',
    (r'^login', 'userLogin'),
    (r'^logout', 'userLogout'),
)

urlpatterns = urlpatterns+patterns('dare.views.daresdata',
    (r'^profile', 'getProfile'),
    (r'^post', 'setPostData'),
    (r'^darestats', 'getDareStats'),
    (r'^friends', 'getMyFriends'),
    (r'^givedaretomyfriend', 'giveDareToMyFriend'),
    (r'^daresfriends/notdone', 'getNotDoneDaresFromFriends'),
    (r'^daresfriends/completed', 'getCompletedDaresFromFriends'),
    (r'^daresfriends/waitingforapproval', 'getWaitingForApprovalDaresFromFriends'),
    (r'^darestofriends/', 'getAllDaresToFriends'),
    (r'^mystats', 'getFullProfile'),
    (r'^checkpost', 'getPostData'),
)

"""

    (r'^daresfriends/completed', 'getCompletedDaresFromFriends'),
    (r'^daresfriends/waitingforapproval', 'getWaitingForApprovalDaresFromFriends'),


"""
