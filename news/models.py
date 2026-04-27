import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#NEWS
class NewsManager(models.Manager):
    def count_by_id(self, id):
        return self.filter(id = id).count()

    def get_by_id(self, id):
       if self.count_by_id(id):
           return super().get_queryset().get(id = id)
       else:
            return None

    def get_by_news_name(self, name):
        if self.filter(name = name).exists():
            return self.get(name = name)
        else:
            return None

class News(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    publisher = models.CharField(max_length=150, null=False, blank=False)
    information = models.TextField(null=False, blank=False)
    attachment = models.FileField(upload_to=path_attachment, null=True, blank=True)
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)
    post_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    post_update = models.DateTimeField(auto_now=True, blank=False, null=False)

    objects = NewsManager()

    class Meta:
        db_table = 'news'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'news/photo/'

    @property
    def upload_file_to(self):
        return 'news/file/'

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.name.replace(" ","")).capitalize()
            name = '{}{}{}'.format('P',newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def file_rename(self):
        try:
            newname = ''.join(self.name.replace(" ","")).capitalize()
            name = '{}{}{}'.format('F',newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def photoname(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    @property
    def filename(self, *args, **kwargs):
        return self.attachment.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = News.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
                    if item.filename != self.attachment.instance.filename:
                        item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(News, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = News.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.attachment.delete(save=False)
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(News, self).delete(*args, **kwargs)
#END OF NEWS