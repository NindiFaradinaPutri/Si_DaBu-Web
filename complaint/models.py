import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *
from profile.models import FAQ

from authentication.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

class ComplaintCategory(models.Model):
    category = models.CharField(max_length = 200, null=False, blank=False)
    information = models.CharField(max_length = 400, null=False, blank=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'complaint_category'
 
    def __str__(self):
        return self.category

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

class Complaint(models.Model):
    subject = models.CharField(max_length = 300, null=False, blank=False)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.CharField(max_length = 200, null=False, blank=False)
    email = models.EmailField(null=True, blank=True)
    telphone = models.CharField(max_length=20, null=True, blank=True)
    information = models.TextField(null=False, blank=False)
    attachment =  models.FileField(upload_to=path_attachment, null=True, blank=True)
    forward_email = models.BooleanField(default=True)    
    creation_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    update_update = models.DateTimeField(auto_now=True, blank=False, null=False)

    class Meta:
        db_table = 'complaint'

    def __str__(self):
        return 'Complaint '+str(self.subject)

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_file_to(self):
        return 'complaint/file/'

    @property
    def file_rename(self):
        try:
            newname = ''.join(self.attachment.name.split('.')[0].replace(" ","")).capitalize()
            name = '{}{}'.format('Complaint',newname)
        except Exception as err:
            name = ''
        return name

    @property
    def filename(self, *args, **kwargs):
        return self.attachment.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            items = Complaint.objects.filter(id = self.id)
            if items:
                for item in items:
                    if item.filename != self.attachment.instance.filename:
                        item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(Complaint, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Complaint.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.attachment.delete(save=False)
        except Exception as e:
            pass
        super(Complaint, self).delete(*args, **kwargs)

class ComplaintStatus(models.Model):
    status = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        db_table = 'complaint_status'
 
    def __str__(self):
        return self.status

class ComplaintResponse(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(UserData, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(ComplaintStatus, on_delete=models.SET_NULL, null=True, blank=True)
    response_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    comment = models.CharField(max_length = 500, null=True, blank=True)

    class Meta:
        db_table = 'complaint_response'

    def __str__(self):
        return self.comment

    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)
    

def contact_us(request):

    menu = ['Home', 'Report']
    title = 'Report'

    contact = Contact.objects.filter(id=1).first()

    faq_items = FAQ.objects.filter(
        is_active=True
    ).order_by('order', 'id')

    form = ComplaintForm()

    return render(
        request,
        'frontend/contact/contact.html',
        {
            'title': title,
            'form': form,
            'contact': contact,
            'faq_items': faq_items,
        }
    )