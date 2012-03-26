from django.http import HttpResponse
import json
import facebookutilities as FB

# Create your views here.
def userLogin(request):
    #print request.GET
    #data = '{"access_token" : "'+str(request.GET.getlist("access_token")[0])+'"}'
    accessToken = FB.getFBAccessToken(request)
    fbId = FB.getFBId(accessToken) 
    print fbId
    return HttpResponse(fbId)
    #return HttpResponse(request.GET)
    #return HttpResponse(request.GET.getlist("access_token"))
    #return HttpResponse(request.GET)
    #return HttpResponse("Welcome to Dares!!")


