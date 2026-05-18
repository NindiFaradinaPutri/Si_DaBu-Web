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
from banner.models import *
from datetime import date
from pathlib import Path

#FORM BANNER
from django import forms
from .models import Event, EventPhoto


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = [
            'name',
            'date',
            'time',
            'location',
            'location_map',
            'information',
            'is_form',
            'url_form'
        ]

        labels = {
            'name': 'Nama Event',
            'date': 'Tanggal Event',
            'time': 'Waktu Event',
            'location': 'Lokasi',
            'location_map': 'Link Google Maps',
            'information': 'Informasi Event',
            'is_form': 'Use Form?',
            'url_form': 'Link Google Form',
        }

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Masukkan nama event'
                }
            ),

            'date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),

            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Contoh: Mall Living Plaza'
                }
            ),

            'location_map': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://www.google.com/maps/embed?pb=...'
                }
            ),

            'information': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Deskripsi atau informasi event'
                }
            ),
            'is_form': forms.CheckboxInput(
                    attrs={
                        'class': 'form-check-input',
                        'id': 'id_is_form'  # 🔥 paksa ID konsisten
                    }
                ),

                'url_form': forms.URLInput(
                    attrs={
                        'class': 'form-control',
                        'placeholder': 'https://your-google-form-link.com'
                    }
                ),
        }

    field_order = [
        'name',
        'date',
        'time',
        'location',
        'location_map',
        'information',
        'is_form',
        'url_form'

    ]


class EventPhotoForm(forms.ModelForm):

    class Meta:
        model = EventPhoto
        fields = [
            'information',
            'photo'
        ]

        labels = {
            'information': 'Keterangan Foto',
            'photo': 'Poster Event'
        }

        widgets = {
            'information': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Contoh: Poster Event'
                }
            ),

            'photo': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            )
        }

    field_order = [
        'information',
        'photo'
    ]