from django.http import HttpResponse
import dare.facebookutilities as FB
from dare.models import *
import django.utils.simplejson as json
import dare.views.users as users

def getPostData(request):
        check = str(request.POST.getlist("check")[0])
        print check
        return HttpResponse(check)

def getProfile(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        syncMemberWithFB(memberId)
        return HttpResponse(json.dumps(getMemberProfile(memberId)))
    else:
        return users.sendInvalidSessionResponse()

def setPostData(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        postId = str(request.GET.getlist("postId")[0])
        memberDareId = str(request.GET.getlist("dareId")[0])
        response = setMemberDarePostData(memberId,memberDareId,postId)
        return HttpResponse(json.dumps(response))
    else:
        return users.sendInvalidSessionResponse()

def getDareStats(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        memberDareId = str(request.GET.getlist("dareId")[0])
        response = getMemberDareStats(memberId,memberDareId)
        return HttpResponse(json.dumps(response))
    else:
        return users.sendInvalidSessionResponse()

def getFullProfile(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        #get memberprofile
        syncMemberWithFB(memberId)
        memberStats = getMemberStats(memberId)
        memberProfile = getMemberProfile(memberId)
        fullMemberProfile = dict(memberProfile.items()+memberStats.items())
        return HttpResponse(json.dumps(fullMemberProfile))
    else:
        return users.sendInvalidSessionResponse()

def getMyFriends(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        #get memberprofile
        syncFriendsWithFB(memberId)
        return HttpResponse(json.dumps(getFriends(memberId)))
    else:
        return users.sendInvalidSessionResponse()

def giveDareToMyFriend(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        friendId = str(request.GET.getlist("friendId")[0])
        dareTitle = str(request.GET.getlist("dareTitle")[0])
        dareDescription = str(request.GET.getlist("dareDescription")[0])
        return HttpResponse(json.dumps(createDareForFriend(memberId,
                        friendId,dareTitle,dareDescription)))
    else:
        return users.sendInvalidSessionResponse()

def getNotDoneDaresFromFriends(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        syncMemberDareFromFriendsWithFB(memberId)
        return HttpResponse(json.dumps(
                    getMemberDaresFromFriendNotPostedList(memberId)))
    else:
        return users.sendInvalidSessionResponse()

def getCompletedDaresFromFriends(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        syncMemberDareFromFriendsWithFB(memberId)
        return HttpResponse(json.dumps(
                    getMemberDaresFromFriendCompletedList(memberId)))
    else:
        return users.sendInvalidSessionResponse()

def getWaitingForApprovalDaresFromFriends(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        syncMemberDareFromFriendsWithFB(memberId)
        return HttpResponse(json.dumps(
                    getMemberDaresFromFriendWFAList(memberId)))
    else:
        return users.sendInvalidSessionResponse()

def getAllDaresToFriends(request):
    memberId = users.getSessionVariable(request)
    if memberId:
        return HttpResponse(json.dumps(
                    getMemberDaresToFriendAllList(memberId)))
    else:
        return users.sendInvalidSessionResponse()

