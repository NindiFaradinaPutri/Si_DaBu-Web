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
from profile.models import *
from datetime import date
from pathlib import Path

from captcha.fields import ReCaptchaField

#Company Profile
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["name","brief","meaning","visi","misi","value","history","culture"]
        labels = {
            'name': 'Nama',
            'brief': 'Deskripsi',
            'visi': 'Visi',
            'misi': 'Misi',
            'value': 'Nilai-Nilai',
            'meaning': 'Makna',
            'culture': 'Budaya',
            'history': 'Sejarah Singkat',
            }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','max_length':100,'disabled': 'True'}),
            'culture':forms.Textarea(attrs={'class':'form-control','rows':3,'disabled': 'True'}),
            'brief':forms.Textarea(attrs={'class':'form-control','rows':3,'disabled': 'True'}),
            'visi':forms.TextInput(attrs={'class':'form-control','max_length':300,'disabled': 'True'}),
            'misi':forms.Textarea(attrs={'class':'form-control','rows':3,'disabled': 'True'}),
            'value':forms.Textarea(attrs={'class':'form-control','disabled': 'True'}),
            'meaning':forms.Textarea(attrs={'class':'form-control','rows':3,'disabled': 'True'}),
            'history':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'disabled': 'True'}),
            }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

    field_order = ["name","brief","visi","misi","value","meaning","history","culture"]
#Company Profile End

#Contact Form
class ContactForm(forms.ModelForm):
    email = forms.EmailField(max_length=150, 
                             widget = forms.EmailInput(attrs={'max_length':150,'class' : 'form-control radiun-10','disabled': 'True'}), help_text="Masukkan email yang valid")
    
    phone_regex = RegexValidator(regex=r'^(^\+62\s?)(\d{3,4}-?){2}\d{3,4}$', message="Nomor harus diawali '+62' dan maksimal 15 digit")

    phone = forms.CharField(label='Nomor Handphone', max_length=20, initial="+62", 
                                 widget=forms.TextInput(attrs = {'class' : 'form-control','disabled': 'True'}),
                                 validators=[phone_regex], help_text='Gunakan format +62')

    whatsapp_regex = RegexValidator(regex=r'^(^\+62\s?)(\d{3,4}-?){2}\d{3,4}$', message="Nomor WhatsApp harus diawali '+62' dan maksimal 15 digit")
    
    whatsapp = forms.CharField(label='Whatsapp', max_length=20, initial="+62", 
                                 widget=forms.TextInput(attrs = {'class' : 'form-control','disabled': 'True'}),
                                 validators=[whatsapp_regex], help_text='Gunakan format +62')

    class Meta:
        model = Contact
        fields = {'address','working_hour','phone','email','whatsapp','instagram','tiktok','facebook','youtube','linkedin','twitter','sla'}
        labels = {
            'address' : 'Alamat Masjid',
            'working_hour' : 'Jam Operasional',
            'email' : 'E-mail',
            'instagram' : 'Instagram',
            'tiktok' : 'Tiktok',
            'facebook' : 'Facebook',
            'youtube' : 'Youtube',
            'linkedin' : 'LinkedIn',
            'twitter' : 'Twitter',
            'sla' : 'SLA',
            }
        widgets = {
            'address':forms.Textarea(attrs={'class':'form-control','max_length':500,'rows':3,'cols':40,'disabled': 'True'}),
            'working_hour':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'instagram':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'tiktok':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'facebook':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'youtube':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'linkedin':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'twitter':forms.TextInput(attrs={'class':'form-control','max_length':150,'disabled': 'True'}),
            'sla':forms.Textarea(attrs={'class':'form-control','max_length':500,'rows':3,'cols':40,'disabled': 'True'}),
            }

    field_order = ['address','working_hour','phone','email','whatsapp','instagram','tiktok','facebook','youtube','linkedin','twitter','sla']

class ReCaptcha(forms.Form):
    captcha = ReCaptchaField(
        public_key=os.environ.get('EMASJID_RECHA_PBC_KEY'),
        private_key=os.environ.get('EMASJID_RECHA_PVT_KEY'),)
#End of Contact Form

class TechnologyForm(forms.ModelForm):
    class Meta:
        model = Technology
        fields = ['name', 'photo']
        labels = {
            'name': 'Name',
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

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question","answer"]
        labels = {
            'question': 'Question',
            'answer': 'Answer',
            }
        widgets = {
            'question':forms.TextInput(attrs={'class':'form-control','max_length':200}),
            'answer':forms.Textarea(attrs={'class':'form-control','rows':3}),
            }

    def __init__(self, *args, **kwargs):
        super(FAQForm, self).__init__(*args, **kwargs)

    field_order = ["question","answer"]