import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#START USER MODEL
class Event(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=250, null=False, blank=False)
    location_map =  models.CharField(max_length=1000, null=False, blank=False)
    information = models.TextField()
    unique_name = models.UUIDField(default=uuid4, editable=False, unique=True)
    is_form = models.BooleanField(default=False)
    url_form =  models.CharField(max_length=1000, null=False, blank=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'event'

    def __str__(self):
        return self.name + "-" + self.date
    
    @property
    def poster(self):
        photo = EventPhoto.objects.filter(id_event = self.id).first()
        if photo:
            return photo.photo.url
        else:
            return ""

class EventPhoto(models.Model):
    id_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False, blank=False)
    information = models.CharField(max_length=100, default="Poster Event", null=True)
    photo = models.ImageField(upload_to=path_and_rename, null=True, verbose_name='')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'event_photo'

    def __str__(self):
        return self.information + " : " + str(self.photo) 

    @property
    def upload_to(self):
        return 'event/'

    @property
    def file_rename(self):
        try:
            newname = ''.join(self.user.username.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except:
            name = ''
        return name

    @property
    def filename(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = EventPhoto.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.filename != self.photo.instance.filename:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(EventPhoto, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = EventPhoto.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(EventPhoto, self).delete(*args, **kwargs)
#END OF USER MODEL