from django.db import models
import os,sys
import django.utils.simplejson as json
import dare.facebookutilities as FB
import general_messages_module as GMTM


#global variables
ID_LENGTH = 255
NAME_LENGTH = 128
ACCESS_TOKEN_LENGTH = 128
GENDER_LENGTH = 20
LOCATION_LENGTH = 512
DESCRIPTION_LENGTH = 8096
FB_POST_ID_LENGTH = 1024
PROJECT_HOME = "/home/natty/djangoprogramming/dares"
IMAGES_LOCATION = os.path.join(PROJECT_HOME,"images")
MEMBER_IMAGE_LOCATION = os.path.join(PROJECT_HOME,"member")
VEDIOS_LOCATION = os.path.join(PROJECT_HOME,"vedios")
DARE_VEDIO_LOCATION = os.path.join(VEDIOS_LOCATION,"dare")

"""
for now we support only level from 0-5
MINIMUM_APPROVALS_COUNTS[levelNumber][friendsCount,OtherMemberCount]
ex: level0 minimum approvals from friends = MINIMUM_APPROVALS_COUNTS[0][0] 

"""
MINIMUM_APPROVALS_COUNTS = [[1,2],[10,4],[20,8],[25,10],[30,12],[35,14]]

"""
minimum dares to be completed to finish a level
"""
MINIMUM_DARES_TO_BE_COMPLETED = [2,10,5,4,3,2]

# Create your models here.
class Member(models.Model):
    id = models.CharField(max_length=ID_LENGTH,primary_key=True)
    curLevelNumber = models.IntegerField(default=0)
    pictureLocation = models.CharField(max_length=LOCATION_LENGTH)
    firstName = models.CharField(max_length=NAME_LENGTH)
    lastName = models.CharField(max_length=NAME_LENGTH)
    gender = models.CharField(max_length=GENDER_LENGTH)
    accessToken = models.CharField(max_length=ACCESS_TOKEN_LENGTH)

    def __unicode__(self):
        return self.firstName
    
    """
    Member get methods
    """
    def getId(self):
        return self.id
    def getCurLevelNumber(self):
        return self.curLevelNumber
    def getFirstName(self):
        return self.firstName
    def getLastName(self):
        return self.lastName
    def getGender(self):
        return self.gender
    def getAccessToken(self):
        return self.accessToken
    
    """
    Member set methods
    """
    def setCurLevelNumber(self,newLevelNumber):
        self.curLevelNumber = newLevelNumber
        self.save()
    def setFirstName(self,fName):
        self.firstName = fName
        self.save()
    def setLastName(self,lName):
        self.lastName = lName
        self.save()
    def setGender(self,memberGender):
        self.gender = memberGender
        self.save()
    def setAccessToken(self,accessToken):
        self.accessToken = accessToken
        self.save()

    def incrementLevel(self):
        self.setCurLevelNumber(self.getCurLevelNumber()+1)


def updateFBAccessToken(memberId,accessToken):
     member = Member.objects.get(pk=memberId)
     member.setAccessToken(accessToken)

def isNewMember(memberId):
    try:
        Member.objects.get(pk=memberId)
    except Member.DoesNotExist:
        return True
    else:
        return False

def createNewMember(fbProfile,fbAccessToken):
    #set up the arguments for new member
    memberId = fbProfile['id']
    """
    TODO: download the picture of member from fb to the pictureLocation
    """
    pictureLocation = os.path.join(IMAGES_LOCATION,memberId+".gif")
    firstName = fbProfile['first_name']
    lastName = fbProfile['last_name']
    gender = fbProfile['gender']

    #create a new member
    member = Member(memberId,0,pictureLocation,firstName,lastName,gender,
            fbAccessToken)
    member.save()

    #assing dares to Member
    assignDaresToMember(member)

"""
method to return Member class object
"""
def getMember(memberId):
    if isNewMember(memberId):
        return None
    else:
        return Member.objects.get(pk=memberId)

def getMemberProfile(memberId):
    member = getMember(memberId)
    memberProfile = {}
    if member is None:
        memberProfile['memberId'] = "unknown"
        memberProfile['first_name'] = "unknown user"
        memberProfile['last_name'] = "unknown user"
        memberProfile['gender'] = "unknown"
        memberProfile['level_number'] = "unknown"
        memberProfile['dares'] = "unknown"
    else:
        memberProfile['memberId'] = member.getId()
        memberProfile['first_name'] = member.getFirstName()
        memberProfile['last_name'] = member.getLastName()
        memberProfile['gender'] = member.getGender()
        memberProfile['level_number'] = member.getCurLevelNumber()
        memberProfile['dares'] = getMemberDaresList(member)
    print memberProfile 
    return memberProfile
    #return json.dumps(memberProfile)



class Dare(models.Model):
    levelNumber = models.IntegerField()
    title = models.CharField(max_length=NAME_LENGTH)
    description = models.TextField()
    vedioOfDescriptionLocation = models.CharField(max_length=LOCATION_LENGTH)

    members = models.ManyToManyField(Member, through = 'MemberDare')
    
    def __unicode__(self):
        return self.title
    """
    get methods
    """
    def getLevelNumber(self):
        return self.levelNumber
    def getTitle(self):
        return self.title
    def getDescription(self):
        return self.description
    def getVedioOfDescriptionLocation(self):
        return self.vedioOfDescriptionLocation

    """
    set methods
    """
    def setLevelNumber(self,levelNumber):
        self.levelNumber = levelNumber
        self.save()
    def setTitle(self,title):
        self.title = title
        self.save()
    def setDescription(self,description):
        self.description = description
        self.save()
    def setVedioOfDiscriptionLocation(self,location):
        self.vedioOfDescriptionLocation = location
        self.save()


def createDare(levelNumber,title,description,vedioOfDescriptionLocation):
    dare = Dare(levelNumber,title,description,vedioOfDescriptionLocation)
    dare.save()
"""
method to return all dares with specified level number
return: a list of dare objects
"""
def getDareObjects(levNumber):
    return Dare.objects.filter(levelNumber=levNumber)

    
    
class MemberDare(models.Model):
    member = models.ForeignKey(Member)
    dare = models.ForeignKey(Dare)
    daredByMemberid = models.CharField(
            max_length=ID_LENGTH,default="dares.com")
    assginedDate = models.DateTimeField(auto_now_add=True)
    isDareCompleted = models.BooleanField(default=False)
    isDarePosted = models.BooleanField(default=False)
    approvalsCount = models.PositiveIntegerField(default=0)
    approvalsNeededCount = models.PositiveIntegerField()
    fbPostId = models.CharField(max_length=FB_POST_ID_LENGTH)
    dareProof = models.CharField(max_length=LOCATION_LENGTH)

    """
    get methods
    """
    def getId(self):
        return self.id
    def getMember(self):
        return self.member
    def getDare(self):
        return self.dare
    def getAssignedDate(self):
        return self.assignedDate
    def getApprovalsCount(self):
        return self.approvalsCount
    def getApprovalsNeededCount(self):
        return self.approvalsNeededCount
    def getLevelNumber(self):
        return self.dare.getLevelNumber()
    def getFBPostId(self):
        return self.fbPostId
    def getDareProofURL(self):
        return self.dareProof
    def getIsPosted(self):
        if self.isPosted():
            return "True"
        else:
            return "False"
    def getIsCompleted(self):
        if self.isCompleted():
            return "True"
        else:
            return "False"
    """
    is methods
    """   
    def isCompleted(self):
        print self.isDareCompleted
        return self.isDareCompleted
    def isPosted(self):
        return self.isDarePosted
    """
    set methods
    """
    def setApprovalsCount(self,count):
        self.approvalsCount = count
        self.save()
    def setApprovalsNeededCount(self,count):
        self.approvalsNeededCount = count
        self.save()
    def setIsCompleted(self,newStatus):
        self.isDareCompleted = newStatus
        self.save()
    def setIsPosted(self,newStatus):
        self.isDarePosted = newStatus
        self.save()
    def setDareProofURL(self,url):
        self.dareProof = url
        self.save()
    def setFBPostId(self,postId):
        self.fbPostId = postId
        self.save()
    
    def updateStats(self):
        if self.isPosted():
            #get the number of likes from FaceBook
            graphAPI = FB.GraphAPI(self.member.getAccessToken())
            likesCount = graphAPI.getLikesCount(self.getFBPostId())
            self.setApprovalsCount(likesCount)
            dare = self.getDare()
            levelNumber = dare.getLevelNumber()
            minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS[levelNumber][0]
            approvalsCount = self.getApprovalsCount()
            approvalsNeededCount = minFriendsApprovalCount - approvalsCount
            if approvalsNeededCount < 0:
                approvalsNeededCount = 0
            self.setApprovalsNeededCount(approvalsNeededCount)
            if self.getApprovalsNeededCount() == 0:
                self.setIsCompleted(True)

    def convertToMap(self):
        retMap = {}
        retMap['dareId'] = self.getId()
        retMap['dareTitle'] = self.dare.getTitle()
        retMap['dareDescription'] = self.dare.getDescription()
        retMap['isDarePosted'] = self.getIsPosted()
        retMap['isDareCompleted'] = self.getIsCompleted()
        return retMap
    
    def convertToStatsMap(self):
        retMap = {}
        retMap['dareId'] = self.getId()
        retMap['dareSampleVedioLocation'] =\
            self.dare.getVedioOfDescriptionLocation()
        retMap['dareLikesCount'] = self.getApprovalsCount()
        retMap['dareLikesNeededCount'] = self.getApprovalsNeededCount()
        retMap['isDarePosted'] = str(self.isPosted())
        retMap['isDareCompleted'] = str(self.isCompleted())

        return retMap
"""
set member dare post data
"""
def setMemberDarePostData(memberId,memberDareId,postId):
    memberDare = MemberDare.objects.get(pk=memberDareId)
    memberDare.setFBPostId(postId)
    memberDare.setIsPosted(True)
    if (memberDare.getMember().getId()) == memberId:
        retStatus,retData = syncMemberDareWithFB(memberDare)
        if retStatus is None:
            #return the error
            memberDare.setFBPostId("")
            memberDare.setIsPosted(False)
            return retData
        else:
            return GMTM.Response().success()
        
    else:
        return GMTM.ModelError().notAuthorizeToPostOnThisDare()
"""
sync the member dare data with facebook likes count
"""
def syncMemberDareWithFB(memberDare):
    if memberDare.isPosted():
        postId = memberDare.getFBPostId()
        #get likes on post
        graphAPI = FB.GraphAPI(memberDare.getMember().getAccessToken())
        likesCount,FBResponse = graphAPI.getLikesCount(postId)
        print "likesCount: ",likesCount,FBResponse
        if likesCount is None:
            #return the error
            return likesCount,FBResponse
        else:
            memberDare.setApprovalsCount(likesCount)
            levelNumber = memberDare.getDare().getLevelNumber()
            minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS[levelNumber][0]
            approvalsCount = memberDare.getApprovalsCount()
            approvalsNeededCount = minFriendsApprovalCount - approvalsCount
            if approvalsNeededCount < 0:
                approvalsNeededCount = 0
            memberDare.setApprovalsNeededCount(approvalsNeededCount)
            if memberDare.getApprovalsNeededCount() == 0:
                memberDare.setIsCompleted(True)
            return likesCount,GMTM.Response().success()
    else:
        retStatus = False
        return retStatus,GMTM.Response().noPostForDareYet()
"""
sync member with FB
"""
def syncMemberWithFB(memberId):
    member = getMember(memberId)
    curLevelNumber = member.getCurLevelNumber()
    memberDareObjects = getMemberDareObjects(member,
            member.getCurLevelNumber())
    responses = []
    for memberDare in memberDareObjects:
        retStatus,retData = syncMemberDareWithFB(memberDare)
        responses.append([retStatus,retData])
    
    #check if level is changed to assingn new dare
    daresApprovedCount = 0
    daresNeedToBeApprovedCount = 0
    memberDareObjects = getMemberDareObjects(member,curLevelNumber)
    for memberDare in memberDareObjects:
        if memberDare.isCompleted():
            daresApprovedCount +=1
    daresNeedToBeApprovedCount = MINIMUM_DARES_TO_BE_COMPLETED[
            curLevelNumber]-daresApprovedCount
    if daresNeedToBeApprovedCount <= 0:
        #code to increase the level here
        member.incrementLevel()
        #assign new level dare
        assignDaresToMember(member)

    return responses

"""
get member dare stats
"""
def getMemberDareStats(memberId,memberDareId):
    memberDare = MemberDare.objects.get(pk=memberDareId)
    if (memberDare.getMember().getId()) == memberId:
        retStatus,retData = syncMemberDareWithFB(memberDare)
        if retStatus is None:
            #return the error
            return retData
        else:
            return memberDare.convertToStatsMap()
    else:
        return GMTM.ModelError().notAuthorizeOnThisDare()

"""
return stats about the member similar to how many dares completed
how many more to be completed to change the level
"""
def getMemberStats(memberId):
    member = getMember(memberId)
    curLevelNumber = member.getCurLevelNumber()
    totalDares = 0
    daresPostedCount = 0
    daresApprovedCount = 0
    daresWaitingForApprovalCount = 0
    daresNeedToBeApprovedCount = 0
    daresNeedToBePostedCount = 0

    memberDareObjects = getMemberDareObjects(member,curLevelNumber)
    totalDares = len(memberDareObjects)
    for memberDare in memberDareObjects:
        if memberDare.isPosted():
            daresPostedCount +=1
        if memberDare.isCompleted():
            daresApprovedCount +=1
    daresWaitingForApprovalCount = daresPostedCount - daresApprovedCount
    daresNeedToBeApprovedCount = MINIMUM_DARES_TO_BE_COMPLETED[
            curLevelNumber]-daresApprovedCount
    if daresNeedToBeApprovedCount <= 0:
        daresNeedToBeApprovedCount = 0
        #code to increase the level here
        member.incrementLevel()
        #assign new level dare
        assignDaresToMember(member)
    daresNeedToBePostedCount = MINIMUM_DARES_TO_BE_COMPLETED[
            curLevelNumber]-daresPostedCount
    if daresNeedToBePostedCount <= 0:
        dareNeedToBePostedCount = 0
    
    #create a hash map of return stats
    memberStats = {}
    memberStats['daresPostedCount'] = daresPostedCount   
    memberStats['daresApprovedCount'] = daresApprovedCount
    memberStats['daresWaitingForApprovalCount'] = daresWaitingForApprovalCount
    memberStats['daresNeedToBeApprovedCount'] = daresNeedToBeApprovedCount
    memberStats['daresNeedToBePostedCount'] = daresNeedToBePostedCount 
    return memberStats
    
"""
method to return a list of dares with level number = levNumber
return: a list, in which every element is a map, with key as 
dare parameter and value as dare value
"""
def getMemberDaresList(member):

    memberId = member.getId()
    curLevelNumber = member.getCurLevelNumber()
    memberDareObjects = getMemberDareObjects(member,curLevelNumber)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares
    
"""
method to return memberDare objects with specified member,level number
"""
def getMemberDareObjects(inputMember,levelNumber):
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,)
    memberDareObjects = []
    
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember)
    for memberDareObject in tempMemberDareObjects:
        if memberDareObject.getLevelNumber() == levelNumber:
            memberDareObjects.append(memberDareObject)

    #will be the when the server crashed after the member creation but
    #before assignment of the dares or level changed
    if len(memberDareObjects) ==0:
        #assing dares to Member
        assignDaresToMember(inputMember)
        tempMemberDareObjects = MemberDare.objects.filter(member=inputMember)
        for memberDareObject in tempMemberDareObjects:
            if memberDareObject.getLevelNumber() == levelNumber:
                memberDareObjects.append(memberDareObject)
        
    print memberDareObjects

    return memberDareObjects
        


"""
method to assign Dare to a Member
Working Here:
"""
def assignDareToMember(inputMember,inputDare,daredBy="dares.com"):
    memberDare = MemberDare(member=inputMember,dare=inputDare,
            approvalsNeededCount=MINIMUM_APPROVALS_COUNTS[
            inputDare.getLevelNumber()][0])
    memberDare.save()

def assignDaresToMember(member):
    print "assignDaresTOMember"
    curLevelNumber = member.getCurLevelNumber()
    #get the all dares with level number = curLevelNumber
    dares = getDareObjects(curLevelNumber)
    for dare in dares:
        assignDareToMember(member,dare)

