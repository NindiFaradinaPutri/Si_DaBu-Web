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
from ads.models import *
from datetime import date
from pathlib import Path

#FORM BANNER
class BannerForm(forms.ModelForm):
    pilihan_is_active = [(0, 'Tidak Tampil'),(1, 'Tampil')]
    pilihan_category = (
        (1,'Halaman Depan'),
        (2,'Wallpaper'),
        (3,'Slider Jumat'),
    )
    is_active = forms.ChoiceField(label='Status', choices=pilihan_is_active, widget=forms.Select(attrs = {'class' : 'form-control'}), initial=1 )
    category = forms.ChoiceField(label='Category', choices=pilihan_category, widget=forms.Select(attrs = {'class' : 'form-control'}), initial=1 )

    class Meta:
        model = Banner
        fields = ['title','category','description','is_active','photo','link']
        labels = {
            'title': 'Judul',
            'category': 'Categori',
            'description': 'Deskripsi',
            'photo': 'Foto Banner',
            'link': 'Link',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':150}),
            'description':forms.Textarea(attrs={'class':'form-control','max_length':200, 'rows': 2}),
            'link':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            }

    field_order = ['title','category','description','is_active','photo','link']
#END OF BANNER

##FORM VIDEO
#class VideoAdsForm(forms.ModelForm):
#    class Meta:
#        model = PhotoVideoAdsPost
#        fields = ['title','video']
#        labels = {
#            'title':'Judul Video',
#            }
#        widgets = {
#            'title':forms.TextInput(attrs={'class':'form-control','max_length':350}),
#            }
#        help_texts = {
#            'video':'Ukuran maksimum file adalah (maks.) 10 mb.'
#            }

#    field_order = ['title','video']

#    def clean_video(self, *args, **kwargs):
#        video = self.cleaned_data.get('video', False)
#        if video:
#            if video.size > settings.VIDEO_UPLOAD_SIZE:
#                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
#            return video

#class PhotoAdsForm(forms.ModelForm):
#    class Meta:
#        model = PhotoVideoAdsPost
#        fields = ['title','photo']
#        labels = {
#            'title':'Judul Foto',
#            }
#        widgets = {
#            'title':forms.TextInput(attrs={'class':'form-control','max_length':350}),
#            }
#        help_texts = {
#            'photo':'Ukuran maksimum foto adalah (maks.) 1 mb. Dan foto berukuran 338x240'
#            }

#    field_order = ['title','photo']

#    def clean_photo(self, *args, **kwargs):
#        photo = self.cleaned_data.get('photo', False)
#        if photo:
#            if photo.size > settings.MAX_UPLOAD_SIZE:
#                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
#            return photo

##END FORM 