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


class IqamahForm(forms.ModelForm):
    pilihan_is_active = [('0', 'Tidak Tampil'), ('1', 'Tampil')]
    is_active = forms.ChoiceField(
        label='Status',
        choices=pilihan_is_active,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = BannerIqamah
        fields = [
            "title",
            "description",
            "photo",
            "is_active",
            "time_shubuh",
            "time_dzuhur",
            "time_ashar",
            "time_maghrib",
            "time_isya",
        ]

        labels = {
            "title": "Judul",
            "description": "Deskripsi",
            'photo': 'Foto Banner',
            "time_shubuh": "Waktu Shubuh",
            "time_dzuhur": "Waktu Dzuhur",
            "time_ashar": "Waktu Ashar",
            "time_maghrib": "Waktu Maghrib",
            "time_isya": "Waktu Isya",
        }

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "time_shubuh": forms.TextInput(attrs={"class": "form-control"}),
            "time_dzuhur": forms.TextInput(attrs={"class": "form-control"}),
            "time_ashar": forms.TextInput(attrs={"class": "form-control"}),
            "time_maghrib": forms.TextInput(attrs={"class": "form-control"}),
            "time_isya": forms.TextInput(attrs={"class": "form-control"}),
        }

        field_order = [
            "title",
            "description",
            "photo",
            "is_active",
            "time_shubuh",
            "time_dzuhur",
            "time_ashar",
            "time_maghrib",
            "time_isya",
        ]

    def __init__(self, *args, **kwargs):
        super(IqamahForm, self).__init__(*args, **kwargs)

        # 🔥 set initial dari instance (True/False → 1/0)
        if self.instance and self.instance.pk:
            self.initial['is_active'] = '1' if self.instance.is_active else '0'

    def clean_is_active(self):
        value = self.cleaned_data['is_active']
        return bool(int(value))   # 🔥 convert "0/1" -> False/True

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Ukuran foto maksimal 5 MB")

        return photo

