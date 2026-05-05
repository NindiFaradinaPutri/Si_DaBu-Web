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
from information.models import *
from datetime import date
from pathlib import Path

class KutipanPilihanForm(forms.ModelForm):
    date = forms.DateField(required=False, label='Tanggal Kutipan', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')

    category_selection = [('Al-Quran','Al-Quran'),('Hadisth','Hadisth'),('Ulama','Ulama')]
    category = forms.ChoiceField(choices= category_selection, widget=forms.Select(attrs={'class' : 'form-control select2'}))

    class Meta:
        model = KutipanPilihan
        fields = ["date","title","source","category","quotes","notes"]
        labels = {
            'title': 'Judul',
            'source': 'Riwayat',
            'quotes': 'Kutipan',
            'notes': 'Catatan',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'source':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'quotes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'notes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(KutipanPilihanForm, self).__init__(*args, **kwargs)

    field_order = ["date","title","source","category","quotes","notes"]

class KhutbahJumatForm(forms.ModelForm):
    date = forms.DateField(required=False, label='Tanggal Khutbah', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')

    class Meta:
        model = KhutbahJumat
        fields = ["date","title","imam","bilal","brief","naration","quotes"]
        labels = {
            'title': 'Judul',
            'imam': 'Imam',
            'bilal': 'Bilal',
            'brief': 'Ringkasan',
            'naration': 'Pesan',
            'quotes': 'Kutipan',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'imam':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'bilal':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'brief':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'naration':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'quotes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(KhutbahJumatForm, self).__init__(*args, **kwargs)

    field_order = ["date","title","imam","bilal","brief","naration","quotes"]

class KhutbahJumatAttachmentForm(forms.ModelForm):

    is_active = forms.BooleanField(label="Lampiran Khutbah Aktif.",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    class Meta:
        model = KhutbahJumatAttachment
        fields = ["name","photo","attachment","is_active"]
        labels = {
            'name': 'Judul Lampiran',
            'photo': 'Foto',
            'attachment': 'Lampiran',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'attachment':forms.FileInput(attrs = {'class':'form-control'}),
            }

    def __init__(self, *args, **kwargs):
        super(KhutbahJumatAttachmentForm, self).__init__(*args, **kwargs)

    field_order = ["name","photo","attachment","is_active"]

class KegiatanMasjidForm(forms.ModelForm):
    is_active = forms.BooleanField(label="Status Khutbah Aktif?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    class Meta:
        model = KegiatanMasjid
        fields = ["title","brief","naration","quotes","is_active"]
        labels = {
            'title': 'Judul',
            'brief': 'Ringkasan',
            'naration': 'Pesan',
            'quotes': 'Kutipan',
            }
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'brief':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'naration':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'quotes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(KegiatanMasjidForm, self).__init__(*args, **kwargs)

    field_order = ["title","brief","naration","quotes","is_active"]

class KegiatanMasjidAttachmentForm(forms.ModelForm):

    is_active = forms.BooleanField(label="lampiran Kegiatan Masjid masih aktif?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    class Meta:
        model = KegiatanMasjidAttachment
        fields = ["name","photo","attachment","is_active"]
        labels = {
            'name': 'Judul',
            'photo': 'Foto',
            'attachment': 'Lampiran',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'attachment':forms.FileInput(attrs = {'class':'form-control'}),
            }

    def __init__(self, *args, **kwargs):
        super(KegiatanMasjidAttachmentForm, self).__init__(*args, **kwargs)

    field_order = ["name","photo","attachment","is_active"]

class RekeningMasjidForm(forms.ModelForm):
    is_active = forms.BooleanField(label="Rekening Masjid Aktif?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    is_primary = forms.BooleanField(label="Rekening Utama?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    class Meta:
        model = RekeningMasjid
        fields = ["no_rek","name","bank","address","is_active","is_primary","notes","transfer_notes"]
        labels = {
            'no_rek': 'No Rekening',
            'name': 'Nama Pemilik Rekening',
            'bank': 'Bank',
            'address': 'Alamat',
            'notes': 'Catatan',
            'transfer_notes': 'Cara Pengiriman',
            }
        widgets = {
            'no_rek':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'name':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'bank':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'address':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'notes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            'transfer_notes':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(RekeningMasjidForm, self).__init__(*args, **kwargs)

    field_order = ["no_rek","name","bank","address","is_active","is_primary","notes","transfer_notes"]

class RekeningMasjidAttachmentForm(forms.ModelForm):

    is_active = forms.BooleanField(label="Lampiran masjid masih aktif?",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    class Meta:
        model = RekeningMasjidAttachment
        fields = ["name","photo","attachment","is_active"]
        labels = {
            'name': 'Judul',
            'photo': 'Foto',
            'attachment': 'Lampiran',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':300}),
            'attachment':forms.FileInput(attrs = {'class':'form-control'}),
            }

    def __init__(self, *args, **kwargs):
        super(RekeningMasjidAttachmentForm, self).__init__(*args, **kwargs)

    field_order = ["name","photo","attachment","is_active"]