
NOT_AUTHORIZE_TO_POST_ON_THIS_DARE = 301
NOT_AUTHORIZE_ON_THIS_DARE = 302
SUCCESS_CODE = 200
NO_POST_FOR_DARE_CODE = 201

class ModelError:
    error = {'error':{'message':"",'type':"",'code':-1}}

    def notAuthorizeToPostOnThisDare(self):
        self.error['error']['message'] = "member is not allowed to post on this dare"
        self.error['error']['type'] = "notAuthorizeToPostOnThisDare"
        self.error['error']['code'] = NOT_AUTHORIZE_TO_POST_ON_THIS_DARE
        return self.error
    def notAuthorizeOnThisDare(self):
        self.error['error']['message'] = "member does not have authorization on this dare"
        self.error['error']['type'] = "notAuthorizeOnThisDare"
        self.error['error']['code'] = NOT_AUTHORIZE_ON_THIS_DARE
        return self.error

class Response:
     message = {'ok':{'message':"",'type':"",'code':0}}

     def success(self):
         self.message['ok']['message'] = "query is successfull"
         self.message['ok']['type'] = "querySuccessFull"
         self.message['ok']['code'] = SUCCESS_CODE
         return self.message
     def noPostForDareYet(self):
         self.message['ok']['message'] = "no post id set for dare yet"
         self.message['ok']['type'] = "noPostForDareYet"
         self.message['ok']['code'] = NO_POST_FOR_DARE_CODE
         return self.message


