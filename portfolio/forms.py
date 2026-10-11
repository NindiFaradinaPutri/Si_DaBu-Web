"""
Definition of forms.
"""

from django import forms
from django.forms import modelformset_factory, formset_factory

from django.contrib import admin
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.forms import AuthenticationForm,  ReadOnlyPasswordHashField
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.password_validation import validate_password 
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import ASCIIUsernameValidator


from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, validate_integer, RegexValidator, URLValidator, MaxValueValidator, MinValueValidator

#Inner Class in App
from portfolio.models import *
from datetime import date
from pathlib import Path

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = {'name','brief','description','is_active'}
        labels = {
            'name': 'Service Name',
            'brief' : 'Service Summary',
            'description':'Service Descriptions',
            'is_active':'Active?'
            }
        widgets = {
            'name':forms.TextInput(attrs={'max_length':150,'class' : 'form-control'}),
            'brief' : forms.Textarea(attrs={'max_length':400, 'class' : 'form-control'}),
            'description': forms.Textarea(attrs={'class' : 'form-control'}),
            'is_active':forms.CheckboxInput(),
            }

    field_order = ['name','brief','description','is_active']

class ServicePhotoForm(forms.ModelForm):
    choice = (('Icon', 'Icon'), ('Image', 'Image'))

    info = forms.ChoiceField(label='Photo Information',choices=choice,widget=forms.Select(attrs={'class': 'form-control select2'}))

    class Meta:
        model = ServicePhoto
        fields = ["info","path"]
        labels = {
            'info': 'Service Information',
            'path': 'Image Directory',
            }
    def __init__(self, *args, **kwargs):
        super(ServicePhotoForm, self).__init__(*args, **kwargs)
        self.fields['info'].widget.attrs.update({'class' : 'form-control','max_length':100,'required':True})

    field_order = ['info','path']
   
class ServicePhotoEditForm(ServicePhotoForm):
    delete_item = forms.BooleanField(label="Delete Image?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs={'class':'bg-red'}), 
                                     help_text="Click if you want to delete the image") 

    field_order = ['info','path','delete_item']


class PortfolioForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.all(),
                                    empty_label=None, 
                                    widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                    label='Service',
                                    required=True, initial=0)

    launching_date = forms.DateField(required=False, label='Launching Date', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')

    class Meta:
        model = Portfolio
        fields = ['service', 'title', 'information', 'owner', 'link', 'is_active', 'launching_date']
        labels = {
            'title': 'Title',
            'information': 'Description',
            'owner': 'Involved Parties',
            'link': 'URL',
            'is_active': 'Active?',
            }

        widgets = {
            'title': forms.TextInput(attrs={'max_length':150, 'class' : 'form-control'}),
            'information': forms.Textarea(attrs={'class' : 'form-control'}),
            'owner': forms.TextInput(attrs={'max_length':150, 'class' : 'form-control'}),
            'link': forms.TextInput(attrs={'max_length':300, 'class' : 'form-control', 'placeholder': 'Optional'}),
            'is_active':forms.CheckboxInput(),
            }

    def __init__(self, *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.fields['service'] = forms.ModelChoiceField(queryset=Service.objects.all(),
                                        empty_label='Sevice', 
                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                        label='Service',
                                        required=True, initial=1)

    field_order = ['service', 'title', 'information', 'owner', 'launching_date', 'link', 'is_active']

class PortfolioAttachmentForm(forms.ModelForm):

    class Meta:
        model = PortfolioAttachment
        fields = ['file','is_main','is_showing']
        labels = {
            'is_main': 'Main Picture?',
            'is_showing': 'Show Picture?',
            }

        widgets = {
            'is_main':forms.CheckboxInput(),
            'is_showing':forms.CheckboxInput(),
            }

    field_order = ['file','is_main','is_showing']

class PortfolioAttachmentEditForm(PortfolioAttachmentForm):
    delete_item = forms.BooleanField(label="Delete Picture?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs={'class':'bg-red'})) 

    field_order = ['file','is_main','is_showing','delete_item']

class TetstimonyForm(forms.ModelForm):
    class Meta:
        model = Testimony
        fields = ['name', 'position', 'companny', 'information', 'photo']
        labels = {
            'name': 'Name',
            'position': 'Position',
            'companny': 'Company',
            'information': 'Information',
            'photo': 'Photo',
            }

        widgets = {
            'name': forms.TextInput(attrs={'max_length':100, 'class' : 'form-control'}),
            'information': forms.Textarea(attrs={'class' : 'form-control', 'rows': 3}),
            'position': forms.TextInput(attrs={'max_length':200, 'class' : 'form-control'}),
            'companny': forms.TextInput(attrs={'max_length':200, 'class' : 'form-control', 'placeholder': 'Optional'}),
            }

        help_texts = {
                'photo':'Max size is 1 MB',
                }

        field_order = ['name', 'position', 'companny', 'information', 'photo']

        def clean_photo(self, *args, **kwargs):
            photo = self.cleaned_data.get('photo', False)
            if photo:
                if photo.size > settings.MAX_UPLOAD_SIZE:
                    raise ValidationError('The image exceeds 1 MB')
                return photo

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'photo']
        labels = {
            'name': 'Nama',
            'photo': 'Foto'
            }

        widgets = {
            'name': forms.TextInput(attrs={'max_length':100, 'class' : 'form-control'}),
            }

        help_texts = {
                'photo':'Max size is 1 MB',\
                }

        field_order = ['name', 'photo']

        def clean_photo(self, *args, **kwargs):
            photo = self.cleaned_data.get('photo', False)
            if photo:
                if photo.size > settings.MAX_UPLOAD_SIZE:
                    raise ValidationError('The image exceeds 1 MB')
                return photo