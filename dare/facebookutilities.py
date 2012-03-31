#This file contains all the function to communicate with facebook
import django.utils.simplejson as json
import urllib2

GRAPH_API_URL = 'https://graph.facebook.com/'

def getFBAccessToken(request):
    return str(request.GET.getlist("access_token")[0])

def getFBProfile(accessToken):
    response = urllib2.urlopen(GRAPH_API_URL+"me?access_token="+
            accessToken)
    fbProfile =json.loads(response.next()) 
    return fbProfile['id'],fbProfile
    #return json.loads(response.next())['id'],response
    

