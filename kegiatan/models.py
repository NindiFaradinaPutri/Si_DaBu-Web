from email.policy import default
import os
from django.db import models
from django.db.models import DateTimeField
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from authentication.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class Kegiatan(models.Model):
    foto = models.ImageField(upload_to=path_photo, null=True, blank=True, verbose_name='')
    video = models.FileField(upload_to=path_video, null=True, blank=True)
    link = models.CharField(max_length=300, null=True, blank=True)
    informasi = models.CharField(max_length=300, null=False, blank=False)
    
    class Meta:
        db_table = 'kegiatan'

    def __str__(self):
        return self.informasi

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_video_to(self):
        return 'kegiatan/video/'

    @property
    def upload_photo_to(self):
        return 'kegiatan/photo/'

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
            items = Kegiatan.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.foto.instance.photoname:
                        item.foto.delete(save=False)
                    if item.videoname != self.video.instance.videoname:
                        item.video.delete(save=False)
        except Exception as e:
            pass
        super(Kegiatan, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Kegiatan.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.video.delete(save=False)
                    item.foto.delete(save=False)
        except Exception as e:
            pass
        super(Kegiatan, self).delete(*args, **kwargs)
        
#kegiatan transaksi

class ChartOfAccountsGroup(models.Model):
    parent_group = models.ForeignKey('self', on_delete=models.CASCADE, related_name='parent_coa_group', blank=True, null=True)
    group_name = models.CharField(max_length=200)

    user_create = models.CharField(max_length=300)
    user_update = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'coa_group_kegiatan'

    def __str__(self):
        return self.group_name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)



class ChartOfAccounts(models.Model):
    account_name_parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='parent_coa', blank=True, null=True)
    account_name = models.CharField(max_length = 300)
    code = models.CharField(max_length=150, unique = True)
    information = models.TextField(null=True, blank=True)
    group = models.ForeignKey(ChartOfAccountsGroup, on_delete=models.CASCADE, blank=False, null=False)
    account_type = models.CharField(max_length=150, null=False, blank=False)

    user_create = models.CharField(max_length=300)
    user_update = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'coa_kegiatan'

    def __str__(self):
        return self.code +'-'+self.account_name

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)


       

class KegiatanAkuntasi(models.Model):
    date = models.DateTimeField(blank=False, null=False, default=datetime.now())
    name = models.CharField(max_length=300, null=False, blank=False, default='Hamba Allah')
    transaction = models.TextField(null=True, blank=True)
    beras = models.FloatField(null=True, blank=True)
    coa = models.ForeignKey(ChartOfAccounts, on_delete=models.DO_NOTHING, null=False, blank=False)
    debet = models.IntegerField(null=True, blank=True)
    credit = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=False, blank=False)
    last_checked = models.BooleanField(default=False)
    order_no = models.IntegerField(default=0)
    user_create = models.CharField(max_length=300)
    user_update = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'kegiatan_akuntasi'

    def __str__(self):
        return self.transaction

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class KegiatanAkuntasiAttachment(models.Model):
    general_ledgers = models.ForeignKey(KegiatanAkuntasi, on_delete= models.CASCADE , null=False, blank=False)
    foto = models.ImageField(upload_to=path_photo, null=True, blank=True, verbose_name='')
    video = models.FileField(upload_to=path_video, null=True, blank=True)
    link = models.CharField(max_length=300, null=True, blank=True)
    informasi = models.CharField(max_length=300, null=True, blank=True)
    
    class Meta:
        db_table = 'kegiatan_akuntasi_attachment'

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
            items = KegiatanAkuntasiAttachment.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.photoname != self.foto.instance.photoname:
                        item.foto.delete(save=False)
                    if item.videoname != self.video.instance.videoname:
                        item.video.delete(save=False)
        except Exception as e:
            pass
        super(KegiatanAkuntasiAttachment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = KegiatanAkuntasiAttachment.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.video.delete(save=False)
                    item.foto.delete(save=False)
        except Exception as e:
            pass
        super(KegiatanAkuntasiAttachment, self).delete(*args, **kwargs)
        
#Menyimpan data keuangan per minggu menggunakan scheduler
        
class KegiatanJurnal(models.Model):
    date = models.DateTimeField(blank=False, null=False, default=datetime.now())
    transaction = models.TextField(null=True, blank=True)
    coa = models.ForeignKey(ChartOfAccounts, on_delete= models.DO_NOTHING, null=False, blank=False)
    debet = models.IntegerField(null=True, blank=True)
    credit = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=False, blank=False)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50)

    gl_order_no = models.IntegerField(default = 0)

    user_create = models.CharField(max_length=300)
    user_update = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)
    
    class Meta:
        db_table = 'kegiatan_jurnal'

    def __str__(self):
        return self.transaction

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class KegiatanAkuntasiHistory(models.Model):
    date = models.DateTimeField(auto_now=True, blank=False, null=False)
    transaction = models.TextField(null=True, blank=True)
    coa = models.ForeignKey(ChartOfAccounts, on_delete= models.DO_NOTHING, null=False, blank=False)
    debit = models.IntegerField(null=True, blank=True)
    credit = models.IntegerField(null=True, blank=True)
    balance = models.IntegerField(null=False, blank=False)
    information = models.TextField(null=False, blank=False)
    
    user_create = models.CharField(max_length=300)
    user_update = models.CharField(max_length=300)
    user_delete = models.CharField(max_length=300)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)
    delete_date = models.DateTimeField(auto_now=True, blank=False, null=False)
    
    class Meta:
        db_table = 'kegiatan_akuntasi_history'

    def __str__(self):
        return self.transaction

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)