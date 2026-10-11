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
from captcha.fields import ReCaptchaField

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, validate_integer, RegexValidator, URLValidator, MaxValueValidator, MinValueValidator

#Inner Class in App
from authentication.models import *
from datetime import date
from pathlib import Path

#REGISTRATION AND PASSWORD
class PublicSignUpForm(forms.ModelForm):
    username = forms.CharField(label='Username',max_length=30, 
                               widget = forms.TextInput(attrs={'max_length':30,'class' : 'form-control radiun-10'}), help_text="Masukan username yang dipilih")
    password = forms.CharField(label='Password',min_length=8, validators = [validate_password], 
                               widget = forms.PasswordInput(attrs={'class' : 'form-control radiun-10'}), help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, dan angka")
    confirm_password = forms.CharField(label='Konfirmasi Password',min_length=8, validators = [validate_password], 
                                       widget = forms.PasswordInput(attrs={'class' : 'form-control radiun-10'}),help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, dan angka")
    email = forms.EmailField(max_length=50, validators = [validate_email], 
                             widget = forms.EmailInput(attrs={'max_length':30,'class' : 'form-control radiun-10'}), help_text="Masukan email yang valid")
    captcha = ReCaptchaField(
        public_key=os.environ.get('SILA_RECHA_PBC_KEY'),
        private_key=os.environ.get('SILA_RECHA_PVT_KEY'),)

    class Meta:
        model = UserData
        exclude = ['is_active','last_login','groups','user_permissions','is_validate','is_staff','is_admin','is_user',]
    
    def compare_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Kedua password tidak sama')
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.compare_password():
            clearPassNoHash = self.cleaned_data.get('password')
            passHash = make_password(clearPassNoHash, None, 'pbkdf2_sha1')
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
        return user

class AdminSignUpForm(forms.ModelForm):
    email = forms.EmailField(label='Email Aktif',max_length=50, validators = [validate_email],help_text="Masukan email yang valid")
    username = forms.CharField(label='Username',max_length=30, help_text="Masukan username yang dipilih")
    password = forms.CharField(label='Password',min_length=8, validators = [validate_password], widget = forms.PasswordInput(), help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, angka, dan simbol")
    confirm_password = forms.CharField(label='Konfirmasi Password',min_length=8, validators = [validate_password], widget = forms.PasswordInput(),help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, angka, dan simbol")

    class Meta:
        model = UserData
        exclude = ['phone_no','is_active','is_admin','last_login','groups','user_permissions','is_staff','is_staff','is_admin','is_user','is_dokter','is_validate']
    
    def __init__(self, *args, **kwargs):
        super(AdminSignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password'].widget.attrs.update({'class' : 'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class' : 'form-control'})

    def compare_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Kedua password tidak sama')
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.compare_password():
            clearPassNoHash = self.cleaned_data.get('password')
            passHash = make_password(clearPassNoHash, None, 'pbkdf2_sha1')
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
        return user

class InitialProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Nama Depan',max_length=150, help_text='Masukan nama depan anda',
                                 widget = forms.TextInput(attrs={'max_length':150,'class' : 'form-control radiun-10'}))
    last_name = forms.CharField(label='Nama Akhir',max_length=150, help_text='Masukan nama akhir anda',
                                 widget = forms.TextInput(attrs={'max_length':150,'class' : 'form-control radiun-10'}))

    class Meta:
        model = UserProfile
        fields = ['first_name','last_name']

class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(min_length=8, validators = [validate_password], widget = forms.PasswordInput(attrs={'class' : 'form-control radiun-10'}), help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, dan angka")
    confirm_password = forms.CharField(min_length=8, validators = [validate_password], widget = forms.PasswordInput(attrs={'class' : 'form-control radiun-10'}),help_text="Password min 8 karakter kombinasi dari huruf kecil, HURUF BESAR, dan angka")

    class Meta:
        model = UserData
        exclude = ['phone_no','email','username','is_active','is_admin','last_login','is_staff','groups','user_permissions','is_validate','is_user',]
        labels = {
            'password': 'Password',
            'confirm_password': 'Konfirmasi Password',
            }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class' : 'form-control'})
        self.fields['confirm_password'].widget.attrs.update({'class' : 'form-control'})

    def compare_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if self.user.check_password(password):
            raise ValidationError('Password tidak boleh sama dengan password sebelumnya')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Kedua password tidak sama')
        
        return True

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.compare_password():
            clearPassNoHash = self.cleaned_data.get('password')
            passHash = make_password(clearPassNoHash, None, 'pbkdf2_sha1')
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username/Email',max_length=30, 
                               widget = forms.TextInput(attrs={'max_length':30,'class' : 'form-control radiun-10'}), help_text="Masukan username/email yang terdaftar")
    password = forms.CharField(label='Password',min_length=8, validators = [validate_password], 
                               widget = forms.PasswordInput(attrs={'class' : 'form-control radiun-10'}))
#END REGISTRATION AND PASSWORD

#FORM USER
class UserChangeForm(forms.ModelForm):
    class Meta:
        model = UserData
        fields = ['username','email']
        exclude = ['password']
        labels = {
            'email': 'Email',
            'username': 'Username',
            }

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class' : 'form-control','placeholder' : 'Masukan Username Anda','readonly':True})
        self.fields['email'].widget.attrs.update({'class' : 'form-control','placeholder' : 'Masukan Email dengan benar.'})

    def clean_password(self):
        return self.initial['password']

class UserProfileForm(forms.ModelForm):
    sex_choices = [(True,'Pria'),(False,'Wanita')]
    sex = forms.ChoiceField(label='Jenis kelamin',choices= sex_choices, widget=forms.Select(attrs = {'class' : 'form-control'}) )

    phone_regex = RegexValidator(regex=r'^(^\+62\s?)(\d{3,4}-?){2}\d{3,4}$', message="Phone harus diawali '+62'. Phone No hanya terbatas sampai 15 digit")
    phone_no = forms.CharField(label='No Telepon', max_length=20, initial="+62", 
                                 widget=forms.TextInput(attrs = {'class' : 'form-control'}),
                                 validators=[phone_regex], help_text='No Telepon diawali dengan +62')

    date_of_birth = forms.DateField(required=False, label='Tanggal Lahir', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = settings.DATE_INPUT_FORMATS, attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Format tanggal lahir yyyy-mm-dd. Contoh: 2022-01-31')

    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','place_of_birth','date_of_birth','sex','phone_no']
        labels = {
            'first_name': 'Nama Depan',
            'last_name': 'Nama Akhir',
            'place_of_birth': 'Tempat Lahir',
            'date_of_birth': 'Jenis Kelamin',
            }
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control','max_length':500,'rows':3,'cols':40}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
            'place_of_birth':forms.TextInput(attrs={'class':'form-control'}),
            }
    
class UserPhotoForm(forms.ModelForm):
    class Meta:
        model = UserPhoto
        fields = ["information","photo"]
        labels = {
            'information': 'Informasi Foto',
            'photo': 'Foto',
            }
        help_texts = {
            'photo': 'Besar maksimum file adalah (max.) 1 mb',
        }

    def __init__(self, *args, **kwargs):
        super(UserPhotoForm, self).__init__(*args, **kwargs)
        self.fields['information'].widget.attrs.update({'class' : 'form-control','readonly' : True})

    def clean_foto_url(self, *args, **kwargs):
        photo = self.cleaned_data.get('photo', False)
        if photo:
            if photo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError('Besar file melebihi batas maks. ukuran file 1 mb')
            return photo

class UserAddressForm(forms.ModelForm):
    negara = forms.ModelChoiceField(queryset=Negara.objects.all(),
                                                        empty_label='Pilihan Negara', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Negara',
                                                        required=True, initial=0)

    provinsi = forms.ModelChoiceField(queryset=Provinsi.objects.all(),
                                                        empty_label='Pilihan Provinsi', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Provinsi',
                                                        required=False, initial=0)

    dati2 = forms.ModelChoiceField(queryset=Dati2.objects.none(),
                                                        empty_label='Pilihan Kota', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kota',
                                                        required=False, initial=0)

    kecamatan = forms.ModelChoiceField(queryset=Kecamatan.objects.none(),
                                                        empty_label='Pilihan Kecamatan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kecamatan',
                                                        required=False, initial=0)

    kelurahan = forms.ModelChoiceField(queryset=Kelurahan.objects.none(),
                                                        empty_label='Pilihan Kelurahan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kelurahan',
                                                        required=False, initial=0)
    class Meta:
        model = UserAddress
        fields = ['address','negara','provinsi','dati2','kecamatan','kelurahan']
        labels = {
            'address' : 'Alamat Detail',
            }
        widgets = {
            'address':forms.Textarea(attrs={'class':'form-control','max_length':500,'rows':3,'cols':40}),
            }
        help_texts = {
            'address':'*opsional',
            }

    def __init__(self, *args, **kwargs):
        selected_address = kwargs.pop('address', None)
        super(UserAddressForm, self).__init__(*args, **kwargs)
        if selected_address:
            self.fields['dati2'] = forms.ModelChoiceField(queryset=Dati2.objects.filter(provinsi = selected_address.provinsi),
                                                        empty_label='Pilihan Kota/Dati II', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kota/Dati II',
                                                        required=False, initial=0)

            self.fields['kecamatan'] = forms.ModelChoiceField(queryset=Kecamatan.objects.filter(dati2 = selected_address.dati2),
                                                        empty_label='Pilihan Kecamatan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kecamatan',
                                                        required=False, initial=0)

            self.fields['kelurahan'] = forms.ModelChoiceField(queryset=Kelurahan.objects.filter(kecamatan = selected_address.kecamatan),
                                                        empty_label='Pilihan Kelurahan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kelurahan',
                                                        required=False, initial=0)

    
    field_order = ['negara','provinsi','dati2','kecamatan','kelurahan','address']

class UserContactForm(UserChangeForm):
    phone_regex = RegexValidator(regex=r'^(^\+62\s?)(\d{3,4}-?){2}\d{3,4}$', message="Phone harus diawali '+62'. Phone No hanya terbatas sampai 15 digit")
    phone_no = forms.CharField(label='No Telepon', max_length=20, initial="+62", 
                                 widget=forms.TextInput(attrs = {'class' : 'form-control'}),
                                 validators=[phone_regex], help_text='No Telepon diawali dengan +62')

    negara = forms.ModelChoiceField(queryset=Negara.objects.all(),
                                                        empty_label='Pilihan Negara', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Negara',
                                                        required=True, initial=0)

    provinsi = forms.ModelChoiceField(queryset=Provinsi.objects.all(),
                                                        empty_label='Pilihan Provinsi', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Provinsi',
                                                        required=False, initial=0)

    dati2 = forms.ModelChoiceField(queryset=Dati2.objects.none(),
                                                        empty_label='Pilihan Kota', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kota',
                                                        required=False, initial=0)

    kecamatan = forms.ModelChoiceField(queryset=Kecamatan.objects.none(),
                                                        empty_label='Pilihan Kecamatan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kecamatan',
                                                        required=False, initial=0)

    kelurahan = forms.ModelChoiceField(queryset=Kelurahan.objects.none(),
                                                        empty_label='Pilihan Kelurahan', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Pilih Kelurahan',
                                                        required=False, initial=0)

    address = forms.CharField(label='Alamat', widget=forms.Textarea(attrs = {'class' : 'form-control'}), help_text='Alamat Saat Ini (opsional)')

    field_order = ['username','email','phone_no','negara','provinsi','dati2','kecamatan','kelurahan','address']

class UserDescriptionForm(forms.ModelForm):
    class Meta:
        model = UserDescription
        fields = ['brief','description']
        labels = {
            'brief' : 'Ringkasan',
            'description' : 'Deskripsi',
            }
        widgets = {
            'brief':forms.Textarea(attrs={'class':'form-control','max_length':500,'rows':2,'cols':40}),
            'description':forms.Textarea(attrs={'class':'form-control','max_length':500,'rows':4,'cols':40}),
            }

    field_order = ['brief','description']
#END FORM USER

class ReCaptcha(forms.Form):
    captcha = ReCaptchaField(
        public_key=os.environ.get('SILA_RECHA_PBC_KEY'),
        private_key=os.environ.get('SILA_RECHA_PVT_KEY'),)


