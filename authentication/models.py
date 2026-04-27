import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

# Create your models here.
class MonthList(models.Model):
    number = models.SmallIntegerField(null=False, blank=False)
    month_name = models.CharField(max_length=50, null=False, blank=False, default='Januari')

    class Meta:
        db_table = 'month_list'

    def __str__(self):
        return self.month_name

#ADDRESS
class Negara(models.Model):
    nama_negara = models.CharField(max_length=150, null=False, blank=False, default='Indonesia')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'negara'

    def __str__(self):
        return self.nama_negara 

class Provinsi(models.Model):
    negara = models.ForeignKey(Negara, on_delete=models.CASCADE, null=False, blank=False)
    kode_provinsi = models.CharField(max_length=10, null=False, blank=False, default='P0001')
    nama_provinsi = models.CharField(max_length=150, null=False, blank=False, default='Kalimantan Timur')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'provinsi'

    def __str__(self):
        return self.nama_provinsi 

class Dati2(models.Model):
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE, null=False, blank=False)
    kode_dati2 = models.CharField(max_length=10, null=False, blank=False, default='D0001')
    nama_dati2 = models.CharField(max_length=150, null=False, blank=False, default='Balikpapan')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'dati2'

    def __str__(self):
        return self.nama_dati2 

class Kecamatan(models.Model):
    dati2 = models.ForeignKey(Dati2, on_delete=models.CASCADE, null=False, blank=False)
    kode_kecamatan = models.CharField(max_length=10, null=False, blank=False, default='C0001')
    nama_kecamatan = models.CharField(max_length=150, null=False, blank=False, default='Balikpapan Kota')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'kecamatan'

    def __str__(self):
        return self.nama_kecamatan 

class Kelurahan(models.Model):
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE, null=False, blank=False)
    kode_kelurahan = models.CharField(max_length=10, null=False, blank=False, default='L0001')
    nama_kelurahan = models.CharField(max_length=150, null=False, blank=False, default='Telaga Sari')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        db_table = 'kelurahan'

    def __str__(self):
        return self.nama_kelurahan 
#END OF ADDRESS

#USER MODEL
class UserDataManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not username or not email or not password:
            raise ValueError('Username, Email, dan Password harus diisi dengan lengkap.')

        user = self.model(email = self.normalize_email(email))

        user.username = user.normalize_username(username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self.db)
        return user

    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()

    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

class UserData(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    is_user = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_validate = models.BooleanField(default=False)
    last_login = models.DateTimeField(verbose_name='last login', blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    objects = UserDataManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email','password']

    class Meta:
        db_table = 'user'
 
    def __str__(self):
        if not self.fullname:
            return self.username
        else:
            return self.fullname

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_superuser(self):
        return self.is_admin

    def get_username(self):
        return super().get_username()

    @property
    def fullname(self):
        rel = self.userprofile_set.all()
        if rel:
            return rel.first().fullname
        else:
            return self.username
        return None

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def encrypt_username(self):
        return hashid.encode(self.username)

class UserProfileManager(models.Manager):
    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()

    def count_by_user(self, user_id):
        return self.filter(user_id = user_id).count()

    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

    def get_by_user(self, user_id):
        if self.count_by_user(user_id = user_id) >= 1:
            return super().get_queryset().get(user_id = user_id)
        else:
            return None

class UserProfile(models.Model):
    married_status_choices = (
        ('Nikah','Nikah'),
        ('Belum Nikah','Belum Nikah'),
        ('Janda','Janda'),
        ('Duda','Duda'),
        )
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    place_of_birth = models.CharField(max_length=150, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.BooleanField(null=True)
    married_status = models.CharField(max_length=50, choices=married_status_choices)
    phone_no = models.CharField(max_length=20, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    objects = UserProfileManager()

    class Meta:
        db_table = 'user_profile'

    def __str__(self):
        return self.first_name +' '+ self.last_name

    @property
    def fullname(self):
        if self.first_name and self.last_name:
            return self.first_name +' '+ self.last_name
        else:
            return None
        return 
   
class UserPhotoManager(models.Manager):
    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()

    def count_by_user(self, user_id):
        return self.filter(user_id = user_id).count()

    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

    def get_by_user(self, user_id):
        if self.count_by_user(user_id = user_id) >= 1:
            return super().get_queryset().get(user_id = user_id)
        else:
            return None

class UserPhoto(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    information = models.CharField(max_length=100, default="Foto Profil", null=True)
    photo = models.ImageField(upload_to=path_and_rename, null=True, verbose_name='')
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    objects = UserPhotoManager()

    class Meta:
        db_table = 'user_photo'

    def __str__(self):
        return self.information + " : " + str(self.photo) 

    @property
    def upload_to(self):
        return 'akun/'

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
            items = UserPhoto.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.filename != self.photo.instance.filename:
                        item.photo.delete(save=False)
        except Exception as e:
            pass
        super(UserPhoto, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = UserPhoto.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.photo.delete(save=False)
        except Exception as e:
            pass
        super(UserPhoto, self).delete(*args, **kwargs)

class UserAddressManager(models.Manager):
    def count_by_id(self, pkid):
        return self.filter(id = pkid).count()

    def count_by_user(self, user_id):
        return self.filter(user_id = user_id).count()

    def get_by_id(self, pkid):
        if self.count_by_id(pkid = pkid) >= 1:
            return super().get_queryset().get(id = pkid)
        else:
            return None

    def get_by_user(self, user_id):
        if self.count_by_user(user_id = user_id) >= 1:
            return super().get_queryset().get(user_id = user_id)
        else:
            return None

class UserAddress(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=False, blank=False)
    address = models.CharField(max_length=500, null=True, blank=True)
    rw = models.CharField(max_length=10, null=True, blank=True)
    rt = models.CharField(max_length=10, null=True, blank=True)
    kelurahan = models.ForeignKey(Kelurahan, on_delete=models.SET_NULL, null=True, blank=True)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.SET_NULL, null=True, blank=True)
    dati2 = models.ForeignKey(Dati2, on_delete=models.SET_NULL, null=True, blank=True)
    provinsi = models.ForeignKey(Provinsi, on_delete=models.SET_NULL, null=True, blank=True)
    zipcode = models.CharField(max_length =50, null=True, blank=True)
    negara = models.ForeignKey(Negara, on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    objects = UserAddressManager()

    class Meta:
        db_table = 'user_address'

    def __str__(self):
        return self.address

class UserDescription(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, null=False, blank=False)
    brief =  models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'user_description'

    def __str__(self):
        return 'Deskripsi '+self.user.username
#END OF USER MODEL