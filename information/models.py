from email.policy import default
import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from authentication.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#MODEL ABSTRACT FOR IMAGE AND FILE 
class AttachmentModel(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    photo = models.ImageField(upload_to=path_photo, null=True, blank=True)
    attachment = models.FileField(upload_to=path_attachment, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def upload_photo_to(self):
        return 'photo/'

    @property
    def upload_file_to(self):
        return 'file/'

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

#INFORMASI SEPUTAR ALQUR'AN, HADIST DAN IBADAH
class KutipanPilihan(models.Model):
    date = models.DateTimeField(blank=False, null=False)
    title = models.CharField(max_length=300, null=True, blank=True)

    source =  models.CharField(max_length=300, null=True, blank=True)
    category =  models.CharField(max_length=300, null=True, blank=True)
    quotes = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'kutipan_pilihan'

    def __str__(self):
        return self.no_rek

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

#INFORMASI SEPUTAR CERAMAH JUMAT
class KhutbahJumat(models.Model):
    date = models.DateTimeField(blank=False, null=False)
    title = models.CharField(max_length=300, null=True, blank=True)

    imam = models.CharField(max_length=200, null=True, blank=True)
    bilal = models.CharField(max_length=200, null=True, blank=True)

    brief = models.TextField(null=True, blank=True)
    naration = models.TextField(null=True, blank=True)
    quotes = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'khutbah_jumat'

    def __str__(self):
        return self.title

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class KhutbahJumatAttachment(AttachmentModel):
    khutbah = models.ForeignKey(KhutbahJumat, on_delete= models.CASCADE, null=False, blank=False)
    is_active = models.BooleanField(default=False)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'khutbah_jumat_attachment'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
    
    @property
    def upload_photo_to(self):
        return 'khutbah_jumat/photo/'

    @property
    def upload_file_to(self):
        return 'khutbah_jumat/file/'

    def save(self, *args, **kwargs):
        try:
            items = KhutbahJumatAttachment.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
                    if item.filename != self.attachment.instance.filename:
                        item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(KhutbahJumatAttachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = KhutbahJumatAttachment.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.attachment.delete(save=False)
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(KhutbahJumatAttachment, self).delete(*args, **kwargs)

#INFORMASI SEPUTAR RENCANA KEGIATAN
class KegiatanMasjid(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    brief = models.TextField(null=True, blank=True)
    naration = models.TextField(null=True, blank=True)
    quotes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'kegiatan_masjid'

    def __str__(self):
        return self.title

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class KegiatanMasjidAttachment(AttachmentModel):
    kegiatan = models.ForeignKey(KegiatanMasjid, on_delete= models.CASCADE, null=False, blank=False)
    is_active = models.BooleanField(default=False)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'kegiatan_masjid_attachment'

    def __str__(self):
        return self.name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
    
    @property
    def upload_photo_to(self):
        return 'kegiatan_masjid/photo/'

    @property
    def upload_file_to(self):
        return 'kegiatan_masjid/file/'

    def save(self, *args, **kwargs):
        try:
            items = KegiatanMasjidAttachment.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
                    if item.filename != self.attachment.instance.filename:
                        item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(KegiatanMasjidAttachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = KegiatanMasjidAttachment.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.attachment.delete(save=False)
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(KegiatanMasjidAttachment, self).delete(*args, **kwargs)

#INFORMASI SEPUTAR REKENING MASJID
class RekeningMasjid(models.Model):
    no_rek = models.CharField(max_length=300, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    bank = models.CharField(max_length=200, null=False, blank=False)
    address = models.TextField(null=False, blank=False)

    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)

    notes = models.TextField(null=True, blank=True)
    transfer_notes = models.TextField(null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'rekening_masjid'

    def __str__(self):
        return self.no_rek

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class RekeningMasjidAttachment(AttachmentModel):
    rekening = models.ForeignKey(RekeningMasjid, on_delete= models.CASCADE, null=False, blank=False)
    is_active = models.BooleanField(default=False)

    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'rekening_masjid_attachment'

    def __str__(self):
        return self.rekening.no_rek

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
    
    @property
    def upload_photo_to(self):
        return 'rekening_masjid/photo/'

    @property
    def upload_file_to(self):
        return 'rekening_masjid/file/'

    def save(self, *args, **kwargs):
        try:
            items = RekeningMasjidAttachment.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.photo.instance.photoname:
                        item.photo.delete(save=False)
                    if item.filename != self.attachment.instance.filename:
                        item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(RekeningMasjidAttachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = RekeningMasjidAttachment.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.attachment.delete(save=False)
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(RekeningMasjidAttachment, self).delete(*args, **kwargs)

