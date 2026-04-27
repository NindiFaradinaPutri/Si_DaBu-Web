import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class Profile(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    brief = models.TextField(null=True, blank=True)
    visi = models.CharField(max_length=300, null=True, blank=True)
    misi = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    meaning = models.TextField(null=True, blank=True)
    history = models.TextField(null=True, blank=True)
    culture = models.TextField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'profile'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class Contact(models.Model):
    working_hour = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    instagram = models.CharField(max_length=150, null=True, blank=True)
    tiktok = models.CharField(max_length=150, null=True, blank=True)
    facebook = models.CharField(max_length=150, null=True, blank=True)
    youtube = models.CharField(max_length=150, null=True, blank=True)
    twitter = models.CharField(max_length=150, null=True, blank=True)
    linkedin = models.CharField(max_length=150, null=True, blank=True)
    sla = models.CharField(max_length=200, null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'contact'

    def __str__(self):
        return self.address

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class Technology(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=False, blank=False)

    class Meta:
        db_table = 'technology'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'technology/photo/'

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
            items = Technology.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Technology, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Technology.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Technology, self).delete(*args, **kwargs)

class FAQ(models.Model):
    question = models.CharField(max_length=200, null=False, blank=False)
    answer = models.TextField(null=False, blank=False)

    class Meta:
        db_table = 'faq'

    def __str__(self):
        return self.question

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)