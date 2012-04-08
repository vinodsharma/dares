#This file contains all the function to communicate with facebook
import django.utils.simplejson as json
import urllib2,urllib

GRAPH_API_URL = 'https://graph.facebook.com/'
FB_TOKEN_ERROR_CODE = 501
FB_OBJECT_DOES_NOT_EXISTS_ERROR_CODE = 502

def getFBAccessToken(request):
    return str(request.GET.getlist("access_token")[0])

def getFBProfile(accessToken):
    try:
        response = urllib2.urlopen(GRAPH_API_URL+"me?access_token="+
            accessToken)
        fbProfile =json.loads(response.next())
        return fbProfile['id'],fbProfile
    except urllib2.HTTPError,error:
        errorResponse = json.loads(error.next())
        errorResponse['error']['code']= FB_TOKEN_ERROR_CODE
        return None,errorResponse
    
    #return json.loads(response.next())['id'],response
class GraphAPIError:
    error = {'error':{'message':"",'type':"",'code':-1}}

    def objectDoesNotExists(self):
        self.error['error']['message'] = "invalid object ID"
        self.error['error']['type'] = "objectDoesNotExits"
        self.error['error']['code'] = FB_OBJECT_DOES_NOT_EXISTS_ERROR_CODE
        return self.error

    def invalidAccessToken(self,fbErrorObject):
        fbErrorObject['error']['code'] = FB_TOKEN_ERROR_CODE
        return fbErrorObject




class GraphAPI:
    def __init__(self,accessToken):
        self.accessToken = accessToken
    
    """
    method to return a object, by default no pagination
    we will support it when needed
    """
    def getObject(self,objectId,pagination=False):
        try:
            response = urllib2.urlopen(GRAPH_API_URL+objectId+"/?access_token="+
                    self.accessToken)
            fbObject = response.next()
            if fbObject == 'false':
                return GraphAPIError().objectDoesNotExists()
            return json.loads(fbObject)

        except urllib2.HTTPError,error:
            errorResponse = json.loads(error.next())
            return GraphAPIError().invalidAccessToken(errorResponse)
    """
    visit url
    """
    def visitURL(self,url):
        try:
            response = urllib2.urlopen(url)
            return json.loads(response.next())
        except urllib2.HTTPError,error:
            errorResponse = json.loads(error.next())
            return GraphAPIError().invalidAccessToken(errorResponse)
    """
    get object data
    return a map with data as key
    """
    def getObjectData(self,path):
        url = GRAPH_API_URL+path+"?access_token="+self.accessToken
        response = self.visitURL(url)
        if response.has_key('data'):
            objectData = response
            while response.has_key("paging") and response['paging'].has_key(
                    'next'):
                print response['paging']
                response = self.visitURL(response['paging']['next'])
                if response.has_key("data"):
                    objectData['data'].extend(response['data'])
                else:
                    return response
            if objectData.has_key('paging'):
                del(objectData['paging'])
            return objectData
        else:
            return response

    """
    create an object and return the id of the object in json format
    """
    def createObject(self,path,data):
        rsp = None
        query_args = data
        query_args['access_token'] = self.accessToken
        request = urllib2.Request(GRAPH_API_URL+path)
        request.add_data(urllib.urlencode(query_args))
        try:
            rsp = urllib2.urlopen(request) 
        except urllib2.HTTPError,error:
            rsp = error
        return rsp.next()
    
    """
    post a comment on a object
    """
    def postComment(self,objectId,comment):
        data = {"message":comment}
        path = objectId+"/comments"
        return self.createObject(path,data)
    """
    post a message on my wall
    """
    def postMessageOnMyWall(self,message):
        data = {"message":message}
        path = "me/feed"
        return self.createObject(path,data)

    """
    returns: number of likes for the objectId
    error: if there is any error, returns None
    """
    def getLikesCount(self,objectId):
        fbObject = self.getObject(objectId)
        if fbObject.has_key("error"):
            return None,fbObject
        else:
            if fbObject.has_key('likes'):
                return fbObject['likes']['count'],fbObject
            else:
                return 0,fbObject  
    """
      return the list of fbFriendIds
    """
    def getFriends(self):
        friendList = self.getObjectData("me/friends")
        if friendList.has_key('data'):
            return friendList['data'],None
        else:
            #when there is error
            return None,friendList


    
