
NOT_AUTHORIZE_TO_POST_ON_THIS_DARE = 301
NOT_AUTHORIZE_ON_THIS_DARE = 302
CANNOT_CREATE_DARE = 303
CANNOT_CREATE_MEMBER_DARE = 304
SUCCESS_CODE = 200
NO_POST_FOR_DARE_CODE = 201
MEMBER_DOES_NOT_EXISTS = 601

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

    def cannotCreateDare(self):
        self.error['error']['message'] = "not able to create dare try again or check log"
        self.error['error']['type'] = "dareCreationError"
        self.error['error']['code'] = CANNOT_CREATE_DARE
        return self.error
    
    def cannotCreateMemberDare(self):
        self.error['error']['message'] = "not able to assign dare to member"
        self.error['error']['type'] = "memberDareCreationError"
        self.error['error']['code'] = CANNOT_CREATE_MEMBER_DARE
        return self.error
    def memberDoesNotExists(self):
        self.error['error']['message'] = "member does not exists"
        self.error['error']['type'] = "memberDoesNotExistsError"
        self.error['error']['code'] = MEMBER_DOES_NOT_EXISTS
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


