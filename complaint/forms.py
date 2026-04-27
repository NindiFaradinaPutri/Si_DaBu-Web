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
from complaint.models import *
from datetime import date
from pathlib import Path

from captcha.fields import ReCaptchaField

class ComplaintForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=ComplaintCategory.objects.filter(is_active = True),
                                                        empty_label='Kategori Laporan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Category',
                                                        required=False, initial=0)

    phone_regex = RegexValidator(regex=r'^(^\+62\s?)(\d{3,4}-?){2}\d{3,4}$', message="Phone number must begin with '+62'. Phone number limited to 15 digits")
    telphone = forms.CharField(label='No Telepon', max_length=20, initial="+62", 
                                 widget=forms.TextInput(attrs = {'class' : 'form-control'}),
                                 validators=[phone_regex],required=True, help_text="Phone number must begin with '+62'")
    captcha = ReCaptchaField(
        public_key=os.environ.get('EMASJID_RECHA_PBC_KEY'),
        private_key=os.environ.get('EMASJID_RECHA_PVT_KEY'),)
    
    class Meta:
        model = Complaint
        fields = ["subject","category","sender","email","telphone","information","attachment"]
        labels = {
            'subject': 'Perihal',
            'sender': 'Nama',
            'email': 'Email',
            'information': 'Informasi',
            'attachment': 'Lampiran',
            }
        widgets = {
            'subject':forms.TextInput(attrs={'class':'form-control','max_length':300,'placeholder':'Required', 'required':'True'}),
            'sender':forms.TextInput(attrs={'class':'form-control','max_length':200,'placeholder':'Required', 'required':'True'}),
            'email':forms.TextInput(attrs={'class':'form-control','placeholder':'Required', 'required':'True'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'The detail about your complaint', 'required':'True'}),
            'attachment':forms.FileInput(attrs = {'class':'form-control'}),
            }
        help_texts = {
            'attachment':'Maximum size is 1 MB or 1.000 KB',
            'information':'Please give us the detail abour your report',
            }

    field_order = ["category","subject","sender","email","telphone","information","attachment"]
    
class ComplaintCategoryForm(forms.ModelForm):
    is_active = forms.BooleanField(
        label="Status Aktif?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'text-dark'}),
        help_text="Centang jika kategori aktif"
    )

    class Meta:
        model = ComplaintCategory
        fields = ["category","information","is_active"]
        labels = {
            'category': 'Nama Kategori',
            'information': 'Informasi',
            }
        widgets = {
            'category':forms.TextInput(attrs={'class':'form-control','max_length':200,'placeholder':'Masukkan nama kategori'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Penjelasan kategori'}),
            }

    field_order = ["category","information","is_active"]

class ComplaintResponseForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserData.objects.all(),
                                    empty_label='User Choice', 
                                    widget=forms.Select(attrs={'class' : 'form-control select2','readonly':True}),
                                    label='User',
                                    required=True)

    status = forms.ModelChoiceField(queryset=ComplaintStatus.objects.all(),
                                    empty_label='Status Choice', 
                                    widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                    label='Laporan Status',
                                    required=True,initial=0)

    class Meta:
        model = ComplaintResponse
        fields = ["user","status","comment"]
        labels = {
            'comment': 'Comment',
            }
        widgets = {
            'comment':forms.Textarea(attrs={'class':'form-control','max_length':300,'rows':3,'cols':40}),
            }

    field_order = ["user","status","comment"]