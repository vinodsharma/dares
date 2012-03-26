from django.http import HttpResponse
import json

# Create your views here.
def userLogin(request):
    #print request.GET
    data = '{"access_token" : "'+str(request.GET.getlist("access_token")[0])+'"}'
    return HttpResponse(data)
    #return HttpResponse(request.GET)
    #return HttpResponse(request.GET.getlist("access_token"))
    #return HttpResponse(request.GET)
    #return HttpResponse("Welcome to Dares!!")


