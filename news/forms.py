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
from news.models import *
from datetime import date
from pathlib import Path

#FORM NEWS
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['name','publisher','information','photo','attachment']
        labels = {
            'name':'Judul',
            'publisher':'Pembuat',
            'information':'Informasi',
            'photo':'Foto Dokumentasi',
            'attachment':'Lampiran',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':150}),
            'publisher':forms.TextInput(attrs={'class':'form-control','max_length':150}),
            'information':forms.Textarea(attrs={'class':'form-control','max_length':300,'rows':3,'cols':40}),
            'attachment':forms.FileInput(attrs = {'class':'form-control'}),
            }
        help_texts = {
            'photo':'Ukuran maksimum file adalah (maks.) 1 mb',
            'attachment':'Ukuran maksimum file adalah (maks.) 1 mb',
            }

    field_order = ['name','publisher','information','photo','attachment']

    def clean_photo(self, *args, **kwargs):
        photo = self.cleaned_data.get('photo', False)
        if photo:
            if photo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return photo

    def clean_attachment(self, *args, **kwargs):
        attachment = self.cleaned_data.get('attachment', False)
        if attachment:
            if attachment.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return attachment
#END OF NEWS