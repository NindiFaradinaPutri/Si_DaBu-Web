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
from team.models import *
from datetime import date
from pathlib import Path

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name','information','position','linkedin','order','photo']
        labels = {
            'name':'Nama',
            'information':'Deskripsi',
            'position':'Posisi',
            'linkedin':'Linkedin Profil URL',
            'order':'Urutan',
            'photo':'Foto',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':100}),
            'information':forms.Textarea(attrs={'class':'form-control','rows': 2, 'max_length':200, 'placeholder': 'Optional'}),
            'position':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'order':forms.TextInput(attrs={'class':'form-control','placeholder':'No Urutan'}),
            'linkedin':forms.TextInput(attrs={'class':'form-control','max_length':300, 'placeholder': 'Optional'}),
            }
        help_texts = {
            'photo':'Ukuran maksimum file adalah (maks.) 1 mb',\
            }

    field_order = ['name','information','position','linkedin','order','photo']

    def clean_photo(self, *args, **kwargs):
        photo = self.cleaned_data.get('photo', False)
        if photo:
            if photo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return photo

class NarationForm(forms.ModelForm):
    class Meta:
        model = TeamNaration
        fields = ["title","brief","naration","quote"]
        labels = {
            'title': 'Judul',
            'brief': 'Deskripsi Singkat',
            'naration': 'Narasi',
            'quote': 'Pesan',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'brief':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'naration':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'quote':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(NarationForm, self).__init__(*args, **kwargs)

    field_order = ["title","brief","naration","quote"]


