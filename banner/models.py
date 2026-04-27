import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#BANNER
class BannerManager(models.Manager):
    def count_by_id(self, id):
        return self.filter(id = id).count()

    def get_by_id(self, id):
       if self.count_by_id(id):
           return super().get_queryset().get(id = id)
       else:
            return None

    def get_by_banner_title(self, title):
        if self.filter(title = title).exists():
            return self.get(title = title)
        else:
            return None
        
class BannerManagerIqamah(models.Manager):
    def count_by_id(self, id):
        return self.filter(id = id).count()

    def get_by_id(self, id):
       if self.count_by_id(id):
           return super().get_queryset().get(id = id)
       else:
            return None

    def get_by_banner_title(self, title):
        if self.filter(title = title).exists():
            return self.get(title = title)
        else:
            return None

class Banner(models.Model):
    category = (
        (1,'Halaman Depan'),
        (2,'Wallpaper'),
        (3,'Slider Jumat'),
    )

    title = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=200, null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    link = models.CharField(max_length=200, null=True, blank=True)
    category = models.IntegerField(max_length=1, choices=category, default=1)
    
    objects = BannerManager()

    class Meta:
        db_table = 'banner'

    def __str__(self):
        return self.title

    @property
    def upload_photo_to(self):
        return 'banner/photo/'

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.title.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def photoname(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    def save(self, *args, **kwargs):
        try:
            items = Banner.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Banner, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Banner.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Banner, self).delete(*args, **kwargs)

    @property
    def category_safe(self):
        if self.category == 1:
            return 'Halaman Depan'
        elif self.category == 2:
            return 'Wallpaper'
        elif self.category == 3:
            return 'Slider Jumat'
        else:
            return '-'

class BannerIqamah(models.Model):
    title = models.CharField(max_length=150, null=False, blank=False)
    description = models.CharField(max_length=200, null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    time_shubuh = models.CharField(max_length=150, null=False, blank=False)
    time_dzuhur = models.CharField(max_length=150, null=False, blank=False)
    time_ashar = models.CharField(max_length=150, null=False, blank=False)
    time_maghrib = models.CharField(max_length=150, null=False, blank=False)
    time_isya = models.CharField(max_length=150, null=False, blank=False)
    
    objects = BannerManagerIqamah()

    class Meta:
        db_table = 'banner_iqamah'

    def __str__(self):
        return self.title

    @property
    def upload_photo_to(self):
        return 'iqamah/photo/'

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.title.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except Exception as err:
            name = ''
        return name

    @property
    def photoname(self, *args, **kwargs):
        return self.photo.name.split('/')[-1]

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    def save(self, *args, **kwargs):
        try:
            old = BannerIqamah.objects.filter(id=self.id).first()
            if old and old.photo and self.photo:
                if old.photo.name != self.photo.name:
                    old.photo.delete(save=False)
        except Exception:
            pass

        super(BannerIqamah, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = BannerIqamah.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(BannerIqamah, self).delete(*args, **kwargs)
#END OF BANNER