import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

# Service
class ServiceManager(models.Manager):
    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()
    
    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

class Service(models.Model):
    name = models.CharField(max_length=200, unique=True)
    brief = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(null=True, default=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    objects = ServiceManager()

    class Meta:
        db_table = 'service'

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_is_active = self.is_active

    @property
    def photo(self):
        rel = self.servicephoto_set.all()
        if rel:
            return rel[0].path
        else:
            return None

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
# End Service

# Service Photo
class ServicePhotoManager(models.Manager):
    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()

    def count_by_service(self, service_id):
        return self.filter(service_id = service_id).count()

    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

    def get_by_service(self, service_id):
        if self.count_by_service(service_id = service_id) >= 1:
            return super().get_queryset().get(service_id = service_id)
        else:
            return None
    def query_by_service(self, service_id):
        if self.count_by_service(service_id = service_id) >= 1:
            return super().get_queryset().filter(service_id = service_id)
        else:
            return None

class ServicePhoto(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    info = models.CharField(max_length=100, default="Foto / Icon Layanan")
    path = models.ImageField(upload_to=path_and_rename, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)
    objects = ServicePhotoManager()

    class Meta:
        db_table = 'service_photo'

    def __str__(self):
        return str(self.service_path)

    @property
    def upload_to(self):
        return 'services/'

    @property
    def file_rename(self):
        try:
            newname = ''.join(self.info.replace(" ","")).capitalize()
            name = '{}{}'.format(newname[:10],str(timestamp()))
        except:
            name = ''
        return name

    @property
    def filename(self, *args, **kwargs):
        return self.path.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = ServicePhoto.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.filename != self.path.instance.filename:
                        item.path.delete(save=False)
        except:pass
        super(ServicePhoto, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = ServicePhoto.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.path.delete(save=False)
        except Exception as e:
            pass
        super(ServicePhoto, self).delete(*args, **kwargs)
# End Service Photo

# Portfolio
class Portfolio(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE,null=False, blank=False)
    title = models.CharField(max_length = 150, null = False, blank = False)
    information = models.TextField(null=True, blank=True)
    owner = models.CharField(max_length = 300, null = False, blank = False)
    link = models.CharField(max_length = 300, null = True, blank = True)
    is_active = models.BooleanField(default=True)
    launching_date = models.DateTimeField(null = True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)
    
    class Meta:
        db_table = 'portfolio'

    def __str__(self):
        return str(self.title) 

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)


class PortfolioAttachment(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,null=False, blank=False)
    file = models.ImageField(upload_to=path_and_rename, null=False, blank=False)
    is_main = models.BooleanField(default=False)
    is_showing = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)
    
    class Meta:
        db_table = 'portfolio_photo'

    def __str__(self):
        return str(self.portfolio.title + ' - ' + self.encrypt_id)

    @property
    def upload_to(self):
        return 'portfolio/'

    @property
    def file_rename(self):
        try:
            newname = ''.join(self.attachment_information[:15]).capitalize()
            name = '{}{}{}'.format('Port',newname[:8],str(timestamp()))
        except:
            name = ''
        return name

    @property
    def filename(self, *args, **kwargs):
        return self.file.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = PortfolioAttachment.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.filename != self.file.instance.filename:
                        item.file.delete(save=False)
        except:pass
        super(PortfolioAttachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = PortfolioAttachment.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.file.delete(save=False)
        except Exception as e:
            pass
        super(PortfolioAttachment, self).delete(*args, **kwargs)

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
# End Portofolio

#Testimony
class Testimony(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    position = models.CharField(max_length=200, null=False, blank=False)
    companny = models.CharField(max_length=200, null=True, blank=True)
    information = models.TextField(null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=False, blank=False)

    class Meta:
        db_table = 'testimony'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'testimony/photo/'

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
            items = Testimony.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Testimony, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Testimony.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Testimony, self).delete(*args, **kwargs)
#End Testimony

#Tags
class PortfolioTags(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE,null=False, blank=False)
    tags = models.CharField(max_length=20, null=True, blank=False)

    class Meta:
        db_table = 'portfolio_tags'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
#End Tags

class Client(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=False, blank=False)

    class Meta:
        db_table = 'client'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'client/photo/'

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
            items = Client.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Client, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Client.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(Client, self).delete(*args, **kwargs)