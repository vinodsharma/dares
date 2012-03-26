from django.db import models
import os,sys

#global variables
ID_LENGTH = 20
NAME_LENGTH = 128
GENDER_LENGTH = 20
LOCATION_LENGTH = 512
DESCRIPTION_LENGTH = 8096
PROJECT_HOME = "/home/natty/djangoprogramming/dares"
IMAGES_LOCATION = os.path.join(PROJECT_HOME,"images")
MEMBER_IMAGE_LOCATION = os.path.join(PROJECT_HOME,"member")
VEDIOS_LOCATION = os.path.join(PROJECT_HOME,"vedios")
DARE_VEDIO_LOCATION = os.path.join(VEDIOS_LOCATION,"dare")

# Create your models here.
class Member(models.Model):
    id = models.CharField(max_length=ID_LENGTH,primary_key=True)
    pictureLocation = models.CharField(max_length=LOCATION_LENGTH)
    firstName = models.CharField(max_length=NAME_LENGTH)
    lastName = models.CharField(max_length=NAME_LENGTH)
    gender = models.CharField(max_length=GENDER_LENGTH)

    def __unicode__(self):
        return self.firstName

class Dare(models.Model):
    levelNumber = models.IntegerField()
    description = models.TextField()
    vedioOfDescriptionLocation = models.CharField(max_length=LOCATION_LENGTH)

    members = models.ManyToManyField(Member, through = 'MemberDare')
    
    def __unicode__(self):
        return self.description

class MemberDare(models.Model):
    member = models.ForeignKey(Member)
    dare = models.ForeignKey(Dare)
    assginedDate = models.DateTimeField(auto_now_add=True)
    isDareCompleted = models.BooleanField(default=False)
    approvedCount = models.PositiveIntegerField(default=0)
    notApprovedCount = models.PositiveIntegerField(default=0)
