import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class Team(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    position = models.CharField(max_length=200, null=False, blank=False)
    information = models.CharField(max_length=200, null=True, blank=True)
    linkedin = models.CharField(max_length=300, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)

    class Meta:
        db_table = 'team'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'team/photo/'

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.name.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def photoname(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = Team.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Team, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Team.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Team, self).delete(*args, **kwargs)

class TeamNaration(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    brief = models.TextField(null=True, blank=True)
    naration = models.TextField(null=True, blank=True)
    quote = models.TextField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'team_naration'

    def __str__(self):
        return self.title

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)