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

# class InitialSelectionInput(forms.ModelForm):
#     pass

# class ShortTextInput(forms.ModelForm):
#     pass

# class LongTextInput(forms.ModelForm):
#     pass

# class NumberInput(forms.ModelForm):
#     pass

# class EmailInput(forms.ModelForm):
#     pass

# class PhoneInput(forms.ModelForm):
#     pass

# class SingleChoiceInput(forms.ModelForm):
#     pass

# class MultipleChoiceInput(forms.ModelForm):
#     pass

# class DropdownInput(forms.ModelForm):
#     pass

# class DateInput(forms.ModelForm):
#     pass

# class TimeInput(forms.ModelForm):
#     pass  

# class DateTimeInput(forms.ModelForm):
#     pass

# class FileUploadInput(forms.ModelForm):
#     pass

# class ImageUploadInput(forms.ModelForm):
#     pass

# class RatingInput(forms.ModelForm):
#     pass

# class BooleanInput(forms.ModelForm):
#     pass

# class LocationInput(forms.ModelForm):
#     pass

