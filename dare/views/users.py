from django.http import HttpResponse
import dare.facebookutilities as FB
from dare.models import *
import django.utils.simplejson as json

SUCCESS_CODE = 200
INVALID_SESSION_CODE = 401
# Create your views here.

"""
method to check if session is valid or not
"""
def isSessionValid(request):
    try: 
        if request.session['memberId']:
            return True
    except KeyError:
        return False
"""
method to set the session variable
"""
def setSessionVariable(request,memberId):
    request.session['memberId'] = memberId

"""
method to get session variaable that is memberId
"""
def getSessionVariable(request):
    if isSessionValid(request):
        return request.session['memberId']
    else:
        return False

def sendInvalidSessionResponse():
    invalidSessionResponse = {}
    invalidSessionResponse['error'] = {'code':INVALID_SESSION_CODE,
        'message':"invalide session, login again!!"}
    return HttpResponse(json.dumps(invalidSessionResponse))

def userLogin(request):
    #print request.GET
    #data = '{"access_token" : "'+str(request.GET.getlist("access_token")[0])+'"}'
    accessToken = FB.getFBAccessToken(request)
    fbId,fbProfile = FB.getFBProfile(accessToken)
    print fbId
    if fbId:
        if isNewMember(fbId):
            createNewMember(fbProfile,accessToken)
        #set the sesison variable
        setSessionVariable(request,fbId)
        return HttpResponse(json.dumps(getMemberProfile(fbId)))
    else:
        return HttpResponse(json.dumps(fbProfile))
        
    #return HttpResponse(request.GET)
    #return HttpResponse(request.GET.getlist("access_token"))
    #return HttpResponse(request.GET)
    #return HttpResponse("Welcome to Dares!!")

def userLogout(request):
    try:
        del request.session['memberId']
    except KeyError:
        pass
    #create a logout response message
    response  = {}
    response["response"] = {'code':SUCCESS_CODE,'message':"logged out successfully"}

    return HttpResponse(json.dumps(response))




