import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from participant.models import Participant
from utils.functions import *
# from utils.utils import *

from event.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#START FORM MODEL
class Form(models.Model):

    id_event = models.ForeignKey(Event,on_delete=models.CASCADE, null=False, blank=False)
    form_name = models.CharField(max_length=150, null=False, blank=False)
    status = models.BooleanField(default=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'form'

    def __str__(self):
        return self.form_name

class FormQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('short_text', 'Short Text'),
        ('long_text', 'Paragraph'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
    
        ('single_choice', 'Single Choice'),   # radio button
        ('multiple_choice', 'Multiple Choice'), # checkbox
        ('dropdown', 'Dropdown'),
    
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date & Time'),
    
        ('file_upload', 'File Upload'),
        ('image_upload', 'Image Upload'),
    
        ('rating', 'Rating / Scale'),
        ('yes_no', 'Yes / No'),
    
        ('location', 'Location (Map)'),
        ]
    id_form = models.ForeignKey(Form, on_delete=models.CASCADE)
    label = models.TextField()
    type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    form_required = models.BooleanField(default=True)
    order = models.IntegerField(default = 0)
    help_text = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'form_question'

    def __str__(self):
        return self.label

class FormQuestionOption(models.Model):
    form_question = models.ForeignKey(FormQuestion, on_delete=models.CASCADE, null=False, blank=False)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    image = models.ImageField(upload_to='options/', null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'form_question_option'

    def __str__(self):
        return self.label

class FormResponse(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, null=True, blank=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=False, blank=False)
    data_response = models.JSONField()
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)
    unique_response = models.UUIDField(default=uuid4, editable=False, unique=True)

    class Meta:
        db_table = 'form_response'

    def __str__(self):
        return self.unique_response


#END OF FORM MODEL