"""
Definition of forms.
"""

from django import forms
from django.forms import modelformset_factory, formset_factory

from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

#Inner Class in App
from finance.models import *
from qurban.models import *
    
class QurbanTypeForm(forms.ModelForm):
    class Meta:
        model = QurbanType
        fields = ['qurban_type','information']
        labels = {
                'qurban_type':'Tipe Qurban',
                'information':'Keterangan',
                }
        widgets = {
            'qurban_type':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Lengkap'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Penjelasan terkait Tipe Qurban', 'required':'True'}),
            }
    
    field_order = ['qurban_type','information']

class ShohibulQurbanForm(forms.ModelForm):
    gender_choices = [
        ('Pria','Pria'),
        ('Wanita','Wanita'),
        ]
    gender = forms.ChoiceField(label='Jenis kelamin',choices= gender_choices, widget=forms.Select(attrs = {'class' : 'form-control'}) )
    
    class Meta:
        model = ShohibulQurban
        fields = ['name','father','gender','information']
        labels = {
                'name':'Shohibul Qurban',
                'father':'Nama Bapak',
                'gender':'Jenis Kelamin',
                'information':'Keterangan',
                }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Lengkap'}),
            'father':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Ayah Kandung'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Informasi Terkait Shohibul Qurban', 'required':'True'}),
            }
    
    field_order = ['name','father','gender','information']

class QurbanForm(forms.ModelForm):
    gender_choices = [
        ('Pria','Pria'),
        ('Wanita','Wanita'),
        ]
    gender = forms.ChoiceField(label='Jenis kelamin',choices= gender_choices, widget=forms.Select(attrs = {'class' : 'form-control'}) )
    
    qurban_date = forms.DateField(required=False, label='Tanggal Qurban', 
                                    input_formats=settings.DATE_INPUT_FORMATS, 
                                    widget=forms.DateInput(format = 'yyyy-mm-dd', attrs = {'class' : 'form-control','type': 'date'}),
                                    help_text='Date Format is yyyy-mm-dd. Example: 2022-01-31')
    
    qurban_type = forms.ModelChoiceField(queryset=QurbanType.objects.all(),
                                                        empty_label='Belum Dipilih', 
                                                        widget=forms.Select(attrs={'class' : 'form-control select2'}),
                                                        label='Tipe Qurban',
                                                        required=True, initial=0)
    
    qurban_group = forms.CharField(label='Group Qurban',max_length=30, 
                                   widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Group Qurban'}),
                                   required=False,
                                   help_text="Termasuk dalam Group Qurban yang mana.")
    
    class Meta:
        model = ShohibulQurban
        fields = ['name','father','gender','information','qurban_type','qurban_group']
        labels = {
                'name':'Shohibul Qurban',
                'father':'Nama Bapak',
                'gender':'Jenis Kelamin',
                'information':'Keterangan',
                }
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Lengkap'}),
            'father':forms.TextInput(attrs={'class':'form-control','placeholder':'Nama Ayah Kandung'}),
            'information':forms.Textarea(attrs={'class':'form-control','rows':3,'cols':40,'placeholder':'Informasi Terkait Shohibul Qurban', 'required':'True'}),
            }
        
    def __init__(self, *args, **kwargs):
        super(QurbanForm, self).__init__(*args, **kwargs)
        selected_qurban = Qurban.objects.filter(shohibul_qurban_id = self.instance.id, is_done = False).first()
        if selected_qurban:
            self.fields['qurban_date'].initial = selected_qurban.qurban_date
            self.fields['qurban_type'].initial = selected_qurban.qurban_type
            self.fields['qurban_group'].initial = selected_qurban.qurban_group
    
    field_order = ['qurban_date','name','father','gender','information','qurban_type','qurban_group']