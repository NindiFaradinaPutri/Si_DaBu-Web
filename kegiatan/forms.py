"""
Definition of forms.
"""

from dataclasses import fields
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
from kegiatan.models import *
from datetime import date
from pathlib import Path

from captcha.fields import ReCaptchaField

class KegiatanForm(forms.ModelForm):
    class Meta:
        model = Kegiatan
        fields = ["foto","video","link","informasi"]
        labels = {
            'foto': 'Photo',
            'video': 'Video',
            'link': 'JenisKegiatan',
            'informasi': 'Information',
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
        super(KegiatanForm, self).__init__(*args, **kwargs)

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
    
#kegiatan transaksi

class COAGroupForms(forms.ModelForm):
    parent_group = forms.ModelChoiceField(queryset=ChartOfAccountsGroup.objects.all(),
                                                        empty_label='Induk Group', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Induk Group',
                                                        required=False, initial=0)

    class Meta:
        model = ChartOfAccountsGroup
        fields = ['parent_group', 'group_name']
        labels = {
            'group_name':'Nama Group',
            }
        widgets = {
            'group_name':forms.TextInput(attrs={'class':'form-control','max_length':200,'placeholder':'Required', 'required':'True'}),
            }
        help_texts = {
            'group_name':'Silahkan tambahkan nama group',
            }

    field_order = ["parent_group","group_name"]
    
class COAForms(forms.ModelForm):
    account_name_parent = forms.ModelChoiceField(queryset=ChartOfAccounts.objects.all(),
                                                        empty_label='Induk COA', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Induk COA',
                                                        required=False, initial=0)

    account_type_selection = [('Kredit','Kredit'),('Debet','Debet')]
    account_type = forms.ChoiceField(choices= account_type_selection, widget=forms.Select(attrs={'class' : 'form-control select2'}))

    group = forms.ModelChoiceField(queryset=ChartOfAccountsGroup.objects.all(),
                                                        empty_label='Group COA', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Group COA',
                                                        required=False, initial=0)

    class Meta:
        model = ChartOfAccounts
        fields = ['account_name_parent','code','account_name','group','information','account_type']
        labels = {
            'account_name':'Nama COA',
            'code':'Kode COA',
            'account_type':'Tipe Akun',
            'information':'Informasi',
            }
        widgets = {
            'account_name':forms.TextInput(attrs={'class':'form-control','max_length':300,'placeholder':'Required', 'required':'True'}),
            'code':forms.TextInput(attrs={'class':'form-control','max_length':150,'placeholder':'Required', 'required':'True'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Penjelasan terkait COA', 'required':'True'}),
            }

    field_order = ['account_name_parent','code','account_name','group','information','account_type']
    
class KegiatanAkuntasiForm(forms.ModelForm):
    coa = forms.ModelChoiceField(queryset=ChartOfAccounts.objects.all(),
                                                        empty_label='COA', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='COA',
                                                        required=False, initial=0)

    date = forms.DateField(required=False, label='Tanggal Transaksi', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')
    
    # beras = forms.DecimalField(required=False, label='Beras', 
    #                             widget=forms.NumberInput(attrs={'class': 'form-control number-mask', 'placeholder': 'Jumlah Beras'}))


    class Meta:
        model = KegiatanAkuntasi
        fields = ['date','coa','name','transaction','beras','debet','credit','balance']
        labels = {
            'transaction':'Transaksi',
            'name':'Nama',
            'beras' : 'Beras',
            'debet':'Debet',
            'credit':'Kredit',
            'balance':'Jumlah',
            }
        widgets = {
            'transaction':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Penjelasan terkait Transaksi', 'required':'True'}),
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Pemberi'}),
            'beras':forms.TextInput(attrs={'class':'form-control','placeholder':'Jumlah Beras'}),
            'debet':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Jumlah Debet'}),
            'credit':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Jumlah Kredit'}),
            'balance':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Saldo', 'required':'True'}),
            }

    field_order = ['date','coa','name','transaction','beras','debet','credit','balance']        

    def save(self, commit=True):
        gl = super().save(commit=False)

        if self.data.get('debet'):
            gl.debet = int(str(self.data.get('debet')).replace('.',''))
        if self.data.get('credit'):
            gl.credit = int(str(self.data.get('credit')).replace('.',''))
        if self.data.get('balance'):
            gl.balance = int(str(self.data.get('balance')).replace('.',''))
        if self.data.get('beras'):
            gl.beras = int(str(self.data.get('beras')).replace('.',''))


        if commit:
            gl.save()

        return gl

class KegiatanAkuntasiAttachmentForm(forms.ModelForm):
    class Meta:
        model = KegiatanAkuntasiAttachment
        fields = ["foto","video","link","informasi"]
        labels = {
            'foto': 'Photo',
            'video': 'Video',
            'link': 'Youtube Link',
            'informasi': 'Information',
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
        super(KegiatanAkuntasiAttachmentForm, self).__init__(*args, **kwargs)

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

class KegiatanJurnalForm(forms.ModelForm):
    coa = forms.ModelChoiceField(queryset=ChartOfAccounts.objects.all(),
                                                        empty_label='COA', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='COA',
                                                        required=False, initial=0)

    date = forms.DateField(required=False, label='Tanggal Transaksi', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')

    is_active = forms.BooleanField(label="Transaksi Aktif.",
                                     required=False,
                                     widget=forms.CheckboxInput(attrs = {'class':'text-red'}),)

    status_choices = [
                            ('Saldo Akhir', 'Saldo Akhir'),
                            ('Tetap', 'Tetap'),
                            ('Perubahan', 'Perubahan'),
                            ('Dihapus', 'Dihapus')]

    status = forms.ChoiceField(choices= status_choices, label='Status',
                                     widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = KegiatanJurnal
        fields = ['is_active','date','coa','transaction','status','debet','credit','balance']
        labels = {
            'transaction':'Transaksi',
            'debet':'Debet',
            'credit':'Kredit',
            'balance':'Jumlah',
            'is_active':'Aktif?',
            }
        widgets = {
            'transaction':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Penjelasan terkait Transaksi', 'required':'True'}),
            'debet':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Jumlah Debet'}),
            'credit':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Jumlah Kredit'}),
            'balance':forms.TextInput(attrs={'class':'form-control number-mask','placeholder':'Saldo', 'required':'True'}),
            }

    field_order = ['is_active','date','coa','transaction','status','debet','credit','balance']
    