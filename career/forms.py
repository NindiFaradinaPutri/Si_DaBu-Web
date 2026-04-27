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

from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, validate_integer, RegexValidator, URLValidator, MaxValueValidator, MinValueValidator

#Inner Class in App
from career.models import *
from datetime import date
from pathlib import Path

#Career Form
class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = ["code","position","description"]
        labels = {
            'code': 'Position Code',
            'position': 'Position',
            'description': 'Description',
            }
        widgets = {
            'code':forms.TextInput(attrs={'class':'form-control','max_length':50}),
            'position':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(CareerForm, self).__init__(*args, **kwargs)

    field_order = ["code","position","description"]

class CareerPhotoForm(forms.ModelForm):
    class Meta:
        model = CareerPhoto
        fields = ['photo']
        labels = {
            'photo':'Photo',
            }
        help_texts = {
            'photo':'Ukuran maksimum file adalah (maks.) 1 mb',
            }

    field_order = ['photo']

    def clean_photo(self, *args, **kwargs):
        photo = self.cleaned_data.get('photo', False)
        if photo:
            if photo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return photo

class CareerDetailForm(forms.ModelForm):
    class Meta:
        model = CareerDetail
        fields = ["title","description"]
        labels = {
            'title': 'Title',
            'description': 'Description',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'description':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(CareerDetailForm, self).__init__(*args, **kwargs)

    field_order = ["title","description"]
#End of Career Form