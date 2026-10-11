import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from portfolio.models import Client
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class Gallery(models.Model):
    foto = models.ImageField(upload_to=path_photo, null=True, blank=True, verbose_name='')
    video = models.FileField(upload_to=path_video, null=True, blank=True)
    link = models.CharField(max_length=300, null=True, blank=True)
    informasi = models.CharField(max_length=300, null=False, blank=False)
    id_client = models.ForeignKey(Client,on_delete=models.CASCADE, null=False, blank=False)
    
    class Meta:
        db_table = 'gallery'

    def __str__(self):
        return self.informasi

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_video_to(self):
        return 'gallery/video/'

    @property
    def upload_photo_to(self):
        return 'gallery/photo/'

    @property
    def video_rename(self):
        try:
            newname = ''.join(self.informasi.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.informasi.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def videoname(self, *args, **kwargs):
        return self.video.name.split('/')[-1]

    @property
    def photoname(self, *args, **kwargs):
        return self.foto.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = Gallery.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.foto.instance.photoname:
                        item.foto.delete(save=False)
                    if item.videoname != self.video.instance.videoname:
                        item.video.delete(save=False)
        except Exception as e:
            pass
        super(Gallery, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Gallery.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.video.delete(save=False)
                    item.foto.delete(save=False)
        except Exception as e:
            pass
        super(Gallery, self).delete(*args, **kwargs)