from django.db import models
import os,sys
import django.utils.simplejson as json

#global variables
ID_LENGTH = 20
NAME_LENGTH = 128
ACCESS_TOKEN_LENGTH = 128
GENDER_LENGTH = 20
LOCATION_LENGTH = 512
DESCRIPTION_LENGTH = 8096
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
MINIMUM_APPROVALS_COUNTS = [[5,2],[10,4],[20,8],[25,10],[30,12],[35,14]]

"""
minimum dares to be completed to finish a level
"""
MINIMUM_DARES_TO_BE_COMPLETED = [20,10,5,4,3,2]

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
    def setFirstName(self,fName):
        self.firstName = fName
    def setLastName(self,lName):
        self.lastName = lName
    def setGender(self,memberGender):
        self.gender = memberGender
    def setAccessToken(self,fbAccessToken):
        self.accessToken = accessToken



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
    def setTitle(self,title):
        self.title = title
    def setDescription(self,description):
        self.description = description
    def setVedioOfDiscriptionLocation(self,location):
        self.vedioOfDescriptionLocation = location


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
    approvedCount = models.PositiveIntegerField(default=0)
    notApprovedCount = models.PositiveIntegerField(default=0)

    """
    get methods
    """
    def getId(self):
        return self.id
    def getMember(self):
        return self.member
    def getDare(self):
        return self.Dare
    def getAssignedDate(self):
        return self.assignedDate
    def getApprovedCount(self):
        return self.approvedCount
    def getNotApprovedCount(self):
        return self.notApprovedCount
    def getLevelNumber(self):
        return self.dare.getLevelNumber()
        
    """
    set methods
    """
    def setApprovedCount(slef,count):
        self.approvedCount = count
    def setNoApprovedCount(self,count):
        self.notApprovedCount = count
    
    def isDareCompleted(self):
        dare = self.getDare()
        levelNumber = dare.getLevelNumber()
        minFriendsApprovalCount = MINIMUM_APPROVALS_COUNTS[levelNumber][0]
        approvedCount = self.getApprovedCount()
        notApprovedCount = self.getNotApprovedCount()
        if approvedCount - notApprovedCount >= minFriendsApprovalCount:
            return True
        else:
            return False

    def convertToMap(self):
        retMap = {}
        retMap['dareId'] = self.getId()
        retMap['dareTitle'] = self.dare.getTitle()
        retMap['dareDescription'] = self.dare.getDescription()
        retMap['dareVedioOfDescriptionLocation'] =\
            self.dare.getVedioOfDescriptionLocation()
        retMap['dareLevelNumber'] = self.dare.getLevelNumber()
        retMap['dareApprovedCount'] = self.getApprovedCount()
        retMap['dareNotApprovedCount'] = self.getNotApprovedCount()

        return retMap
        
"""
method to return a list of dares with level number = levNumber
return: a list, in which every element is a map, with key as 
dare parameter and value as dare value
"""
def getMemberDaresList(member):
    memberId = member.getId()
    curLevelNumber = member.getCurLevelNumber()
    memberDareObjects = getMemberDareObjects(memberId,curLevelNumber)
    retMemberDares = []
    for memberDareObject in memberDareObjects:
        retMemberDare = memberDareObject.convertToMap()
        retMemberDares.append(retMemberDare)
    return retMemberDares
    
"""
method to return memberDare objects with specified memberId,level number
"""
def getMemberDareObjects(inputMember,levelNumber):
    tempMemberDareObjects = MemberDare.objects.filter(member=inputMember)
    memberDareObjects = []
    for memberDareObject in tempMemberDareObjects:
        if memberDareObject.getLevelNumber() == levelNumber:
            memberDareObjects.append(memberDareObject)

    return memberDareObjects
        


"""
method to assign Dare to a Member
Working Here:
"""
def assignDareToMember(inputMember,inputDare,daredBy="dares.com"):
    memberDare = MemberDare(member=inputMember,dare=inputDare)
    memberDare.save()

def assignDaresToMember(member):
    curLevelNumber = member.getCurLevelNumber()
    #get the all dares with level number = curLevelNumber
    dares = getDareObjects(curLevelNumber)
    for dare in dares:
        assignDareToMember(member,dare)

