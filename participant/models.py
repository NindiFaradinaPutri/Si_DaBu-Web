import email
import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from event.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#START PARTICIPANT MODEL

class StatusParticipant(models.Model):
    status_name = models.CharField(max_length=100)
    information = models.CharField(max_length=225)

    class Meta:
        db_table = 'status_participant'

    def __str__(self):
        return self.status_name

class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    status_user_id = models.ForeignKey(StatusParticipant, on_delete=models.SET_NULL,null=True, blank=True)
    unique_user = models.UUIDField(default=uuid4, editable=False, unique=True)
    id_event = models.ForeignKey(Event,on_delete=models.CASCADE, null=False, blank=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'participant'

    def __str__(self):
        return self.name
    
    @property
    def status(self):
        status = StatusParticipant.objects.filter(id = self.status_user_id.id).first()
        if status:
            return status.status_name
        else:
            return ""

#END OF PARTICIPANT MODEL