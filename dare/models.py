from django.db import models
import os,sys
import django.utils.simplejson as json
import dare.facebookutilities as FB
import general_messages_module as GMTM

"""
Assumptions: for dare to friends level will be 1000
minimum likes needed are 5
"""
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
START_LELVEL = 1

"""
for now we support only level from 1-3
MINIMUM_APPROVALS_COUNTS[levelNumber][friendsCount,OtherMemberCount]
ex: level0 minimum approvals from friends = MINIMUM_APPROVALS_COUNTS[0][0] 

"""
MINIMUM_APPROVALS_COUNTS = [[5,2],[5,4],[5,8]]
MINIMUM_APPROVALS_COUNTS_FOR_DARE_BY_FRIEND = 5
DARE_BY_FRIEND_LEVEL = 1000
"""
minimum dares to be completed to finish a level
"""
MINIMUM_DARES_TO_BE_COMPLETED = [5,4,3,3]

# Create your models here.

class Member(models.Model):
    id = models.CharField(max_length=ID_LENGTH,primary_key=True)
    curLevelNumber = models.IntegerField(default=0)
    pictureLocation = models.CharField(max_length=LOCATION_LENGTH)
    firstName = models.CharField(max_length=NAME_LENGTH)
    lastName = models.CharField(max_length=NAME_LENGTH)
    gender = models.CharField(max_length=GENDER_LENGTH)
    accessToken = models.CharField(max_length=ACCESS_TOKEN_LENGTH)
    
    friends = models.ManyToManyField("self",through="FriendShip",
            symmetrical=False)

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

def isMemberExists(memberId):
    try:
        Member.objects.get(pk=memberId)
    except Member.DoesNotExist:
        return False
    else:
        return True

def isNewMember(memberId):
    if isMemberExists(memberId):
        return False
    else:
        return True

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
    member = Member(memberId,START_LELVEL,pictureLocation,firstName,lastName,
            gender,fbAccessToken)
    member.save()

    #sync friends with facebook
    syncFriendsWithFB(memberId)
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

class FriendShip(models.Model):
    fromMember = models.ForeignKey('Member', related_name='fromMembers')
    toMember = models.ForeignKey('Member', related_name='toMembers')

    def getFriend(self):
        return self.toMember
"""
add a friend
"""
def addFriend(memberId,friendId):
    if isFriendShipExists(memberId,friendId) == False:
        if isMemberExists(friendId):
            friendShip1 = FriendShip(fromMember=getMember(memberId),
                    toMember=getMember(friendId))
            friendShip1.save()
            friendShip2 = FriendShip(fromMember=getMember(friendId),
                    toMember=getMember(memberId))
            friendShip2.save()
"""
add facebook friends if they have account on dares and are not already
friends
"""
def syncFriendsWithFB(memberId):
    graphAPI = FB.GraphAPI(getMember(memberId).getAccessToken())
    fbFriends,error = graphAPI.getFriends()
    if fbFriends and (len(fbFriends) > 0):
        for fbFriend in fbFriends:
            addFriend(memberId,fbFriend['id'])


"""
check if friendship exits
"""
def isFriendShipExists(memberId,friendId):
    friendShip1 = FriendShip.objects.filter(fromMember=getMember(memberId),
            toMember=getMember(friendId))
    friendShip2 = FriendShip.objects.filter(fromMember=getMember(friendId),
            toMember=getMember(memberId))
    if (len(friendShip1) > 0) or (len(friendShip2) > 0):
        return True
    else:
        return False

"""
return my all friends 
"""
def getFriends(memberId):
    friendShips = FriendShip.objects.filter(fromMember=getMember(memberId))
    friends = []
    for friendShip in friendShips:
        friend = {}
        friendObject = friendShip.getFriend()
        friend["first_name"]=friendObject.getFirstName()
        friend["last_name"]=friendObject.getLastName()
        friend["memberId"]=friendObject.getId()
        friends.append(friend)
    friendsdict = {'friends':friends}
    return friendsdict


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
    daredById = models.CharField(
            max_length=ID_LENGTH,default="dares.com")
    isDaredByFriend = models.BooleanField(default=False)
    isDareAccepted = models.BooleanField(default=True)
    assginedDate = models.DateTimeField(auto_now_add=True)
    isDareCompleted = models.BooleanField(default=False)
    isDarePosted = models.BooleanField(default=False)
    approvalsCount = models.PositiveIntegerField(default=0)
    approvalsNeededCount = models.PositiveIntegerField()
    fbPostId = models.CharField(max_length=FB_POST_ID_LENGTH)
    dareProof = models.CharField(max_length=LOCATION_LENGTH)
    
    def __unicode__(self):
        return str(self.id)

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
    def getDaredById(self):
        return self.daredById
    """
    is methods
    """   
    def isCompleted(self):
        print self.isDareCompleted
        return self.isDareCompleted
    def isPosted(self):
        return self.isDarePosted
    def isByFriend(self):
        return self.isDaredByFriend
    def isAccepted(self):
        return self.isDareAccepted
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
    def setIsAccepted(self,value):
        self.isDareAccepted = value
        self.save()

    
    def updateStats(self):
        if self.isPosted():
            #get the number of likes from FaceBook
            graphAPI = FB.GraphAPI(self.member.getAccessToken())
            likesCount = graphAPI.getLikesCount(self.getFBPostId())
            self.setApprovalsCount(likesCount)
            dare = self.getDare()
            levelNumber = dare.getLevelNumber()
            minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS[levelNumber-1][0]
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
        retMap['isDaredByFriend'] = str(self.isByFriend())
        if self.isByFriend():
            retMap['isDareAccepted'] = str(self.isAccepted())
            retMap['daredById'] = self.getDaredById()
            retMap['daredByFirstName'] = getMember(self.getDaredById()).getFirstName()
            retMap['daredByLastName'] = getMember(self.getDaredById()).getLastName()
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
        retMap['isDaredByFriend'] = str(self.isByFriend())
        if self.isByFriend():
            retMap['isDareAccepted'] = str(self.isAccepted())
            retMap['daredById'] = self.getDaredById()
            retMap['daredByFirstName'] = getMember(self.getDaredById()).getFirstName()
            retMap['daredByLastName'] = getMember(self.getDaredById()).getLastName()

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
            if memberDare.isByFriend():
              minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS_FOR_DARE_BY_FRIEND
            else:
              minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS[levelNumber-1][0]
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
            curLevelNumber-1]-daresApprovedCount
    if daresNeedToBeApprovedCount <= 0:
        #code to increase the level here
        member.incrementLevel()
        #assign new level dare
        assignDaresToMember(member)

    return responses

"""
sync member dares from friends with FB
"""
def syncMemberDareFromFriendsWithFB(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendPostedObjects(member)
    responses = []
    for memberDare in memberDareObjects:
        retStatus,retData = syncMemberDareWithFB(memberDare)
        responses.append([retStatus,retData])

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
            curLevelNumber-1]-daresApprovedCount
    if daresNeedToBeApprovedCount <= 0:
        daresNeedToBeApprovedCount = 0
        #code to increase the level here
        member.incrementLevel()
        #assign new level dare
        assignDaresToMember(member)
    daresNeedToBePostedCount = MINIMUM_DARES_TO_BE_COMPLETED[
            curLevelNumber-1]-daresPostedCount
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
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=False)
    for memberDareObject in tempMemberDareObjects:
        if memberDareObject.getLevelNumber() == levelNumber:
            memberDareObjects.append(memberDareObject)

    #will be the when the server crashed after the member creation but
    #before assignment of the dares or level changed
    if len(memberDareObjects) ==0:
        #assing dares to Member
        assignDaresToMember(inputMember)
        tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
                isDaredByFriend=False)
        for memberDareObject in tempMemberDareObjects:
            if memberDareObject.getLevelNumber() == levelNumber:
                memberDareObjects.append(memberDareObject)
        
    print memberDareObjects

    return memberDareObjects
        
"""
method to return all  memberDare from friends
"""
def getMemberDareFromFriendObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares


"""
method to return memberDare from friends which are accepted by me
"""
def getMemberDareFromFriendAcceptedObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=True)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendAcceptedList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendAcceptedObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares

"""
method to return memberDare from friends which are not accepted
"""
def getMemberDareFromFriendNotAcceptedObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=False)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendNotAcceptedList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendNotAcceptedObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares

"""
method to return posted memberDare from friends
"""
def getMemberDareFromFriendPostedObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=True,isDarePosted=True)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendPostedList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendPostedObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares

"""
method to return not posted memberDare from friends
"""
def getMemberDareFromFriendNotPostedObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=True,isDarePosted=False)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendNotPostedList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendNotPostedObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    retMemberDaresDict = {'dares':retMemberDares}
    return retMemberDaresDict

"""
method to return completed memberDare from friends 
"""
def getMemberDareFromFriendCompletedObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=True,isDarePosted=True,
            isDareCompleted=True)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendCompletedList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendCompletedObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    retMemberDaresDict = {'dares':retMemberDares}
    return retMemberDaresDict

"""
method to return waiting for approval memberDare from friends 
"""
def getMemberDareFromFriendWFAObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember,
            isDaredByFriend=True,isDareAccepted=True,isDarePosted=True,
            isDareCompleted=False)
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresFromFriendWFAList(memberId):

    member = getMember(memberId)
    memberDareObjects = getMemberDareFromFriendWFAObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    retMemberDaresDict = {'dares':retMemberDares}
    return retMemberDaresDict

"""
method to return all dares given by me to friends
"""
def getMemberDareToFriendAllObjects(inputMember):
    memberDareObjects = []
    tempMemberDareObjects = MemberDare.objects.filter(isDaredByFriend=True,
            daredById=inputMember.getId())
    for memberDareObject in tempMemberDareObjects:
        memberDareObjects.append(memberDareObject)
    return memberDareObjects

def getMemberDaresToFriendAllList(memberId):
    member = getMember(memberId)
    memberDareObjects = getMemberDareToFriendAllObjects(member)
    
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        del retMemberDare['daredByFirstName']
        del retMemberDare['daredByLastName']
        friend = memberDareObject.getMember()
        retMemberDare['daredToFirstName'] = friend.getFirstName()
        retMemberDare['daredToLastName'] = friend.getLastName()
        retMemberDares.append(retMemberDare)
    retMemberDaresDict = {'dares':retMemberDares}
    return retMemberDaresDict


"""
method to assign Dare to a Member
"""
def assignDareToMember(inputMember,inputDare,daredBy="dares.com"):
    memberDare = MemberDare(member=inputMember,dare=inputDare,
            approvalsNeededCount=MINIMUM_APPROVALS_COUNTS[
            inputDare.getLevelNumber()-1][0])
    memberDare.save()

def assignDaresToMember(member):
    print "assignDaresTOMember"
    curLevelNumber = member.getCurLevelNumber()
    #get the all dares with level number = curLevelNumber
    dares = getDareObjects(curLevelNumber)
    for dare in dares:
        assignDareToMember(member,dare)

def createDareForFriend(memberId,friendId,dareTitle,dareDescription):
    inputMember = getMember(memberId)
    print "createDareForFriend: friendId",friendId
    print "createDareForFriend: memberId",memberId
    print "createDareForFriend: type",type(friendId)
    print "createDareForFriend: type",type(memberId)
    print "createDareForFriend: isMemberExists",isMemberExists(friendId)
    print "createDareForFriend: isMemberExists",isMemberExists(memberId)
    if not isMemberExists(friendId):
        return  GMTM.ModelError().memberDoesNotExists()
    inputFriend = getMember(friendId)
    try:
        inputDare = Dare(levelNumber=DARE_BY_FRIEND_LEVEL,title=dareTitle,
                description=dareDescription,vedioOfDescriptionLocation=
                dareTitle+".3gp")
        inputDare.save()
    except:
        return GMTM.ModelError().cannotCreateDare()
    try:
        memberDare = MemberDare(member=inputFriend,dare=inputDare,
                approvalsNeededCount=MINIMUM_APPROVALS_COUNTS_FOR_DARE_BY_FRIEND,
                isDaredByFriend=True,isDareAccepted=True,daredById = memberId)
        memberDare.save()
    except:
        return GMTM.ModelError().cannotCreateMemberDare()

    return GMTM.Response().success()

