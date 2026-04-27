
from email.policy import default
from django.db import models
from utils.functions import *
from utils.utils import *

from authentication.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

    
#QURBAN
class QurbanType(models.Model):
    qurban_type = models.CharField(max_length=300, null=True, blank=True)
    information = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'qurban_type'

    def __str__(self):
        return self.information

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class ShohibulQurban(models.Model):
    gender_choices = (
        ('Pria','Pria'),
        ('Wanita','Wanita'),
        )
    
    name = models.CharField(max_length=300, null=False, blank=False)
    father = models.CharField(max_length=300, null=False, blank=False)
    gender = models.CharField(max_length=50, choices=gender_choices)
    information = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'shohibul_qurban'

    def __str__(self):
        if gender == 'Wanita':
            return self.name +' binti '+ self.qurban_year
        else:
            return self.name +' bin '+ self.qurban_year

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class Qurban(models.Model):
    shohibul_qurban = models.ForeignKey(ShohibulQurban, on_delete= models.CASCADE , null=False, blank=False)
    qurban_date = models.DateTimeField(default=datetime.now(), null=False, blank=False)
    qurban_type = models.ForeignKey(QurbanType, on_delete=models.CASCADE, null=False, blank=False)
    qurban_group = models.CharField(max_length=300, null=True, blank=True)
    barcode = models.ImageField(upload_to='barcode/', null=True, blank=True)
    is_done = models.BooleanField(default=False, blank=True, null=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True, blank=False, null=False)
    
    class Meta:
        db_table = 'qurban'

    def __str__(self):
        return self.shohibul_qurban +' - '+ self.qurban_year

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
    
    @property
    def upload_photo_to(self):
        return 'barcode/'
    
    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.shohibul_qurban.replace(" ","")).upper()
            name = '{}{}'.format('QR-',newname)
        except Exception as err:
            name = ''
        return name
    
    @property
    def photoname(self, *args, **kwargs):
        return self.barcode.name.split('/')[-1]


    def save(self, *args, **kwargs):
        try:
            items = Qurban.objects.filter(id=self.id)
            if items:
                for item in items:
                    if item.barcode != self.barcode.instance.photoname:
                        item.barcode.delete(save=False)
        except:
            pass
        super(Qurban, self).save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        try:
            items = Qurban.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.barcode.delete(save=False)
        except Exception as e:
            pass
        super(Qurban, self).delete(*args, **kwargs)