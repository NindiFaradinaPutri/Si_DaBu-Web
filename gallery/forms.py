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
from gallery.models import *
from datetime import date
from pathlib import Path

class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ["foto","video","link","informasi"]
        labels = {
            'foto': 'Foto',
            'video': 'Video',
            'link': 'Youtube Link',
            'informasi': 'Informasi',
            }
        widgets = {
            'link':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'informasi':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40}),
            }
        help_texts = {
            'foto':'Ukuran maksimum file adalah (maks.) 1 mb.',
            'video':'Ukuran maksimum file adalah (maks.) 100 mb.',
            'link':'Contoh format link adalah https://www.youtube.com/watch?v=bbnVLJRgzaE'
            }

    def __init__(self, *args, **kwargs):
        super(GalleryForm, self).__init__(*args, **kwargs)

    def clean_photo(self, *args, **kwargs):
        photo = self.cleaned_data.get('foto', False)
        if photo:
            if photo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return photo

    def clean_video(self, *args, **kwargs):
        video = self.cleaned_data.get('video', False)
        if video:
            if video.size > settings.VIDEO_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 100 mb')
            return video

    field_order = ["foto","video","link","informasi"]