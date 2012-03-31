from django.http import HttpResponse
import dare.facebookutilities as FB
from dare.models import *
import django.utils.simplejson as json

# Create your views here.
def userLogin(request):
    #print request.GET
    #data = '{"access_token" : "'+str(request.GET.getlist("access_token")[0])+'"}'
    accessToken = FB.getFBAccessToken(request)
    fbId,fbProfile = FB.getFBProfile(accessToken)
    print fbId
    if isNewMember(fbId):
        createNewMember(fbProfile,accessToken)
    
    return HttpResponse(json.dumps(getMemberProfile(fbId)))
    #return HttpResponse(request.GET)
    #return HttpResponse(request.GET.getlist("access_token"))
    #return HttpResponse(request.GET)
    #return HttpResponse("Welcome to Dares!!")






