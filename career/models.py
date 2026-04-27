import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *
from datetime import datetime

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class Career(models.Model):
    code = models.CharField(max_length=50, null=False, blank=False)
    position = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    class Meta:
        db_table = 'career'

    def __str__(self):
        return self.position

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class CareerPhoto(models.Model):
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)

    class Meta:
        db_table = 'career_photo'

    def __str__(self):
        return str(self.photo)

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'career/'

    @property
    def photo_rename(self):
        try:
            newname = str(timestamp())
            name = '{}{}'.format('Career',newname)
        except Exception as err:
            name = ''
        return name

    @property
    def photoname(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = CareerPhoto.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(CareerPhoto, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = CareerPhoto.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(CareerPhoto, self).delete(*args, **kwargs)

class CareerDetail(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    class Meta:
        db_table = 'career_detail'

    def __str__(self):
        return self.title

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)