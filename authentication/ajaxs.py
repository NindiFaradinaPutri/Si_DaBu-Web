from authentication.models import *
from authentication.forms import *
from utils.utils import *
from app.decorators import *

import json

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.urls import reverse

from django.db.models import Q, BooleanField, CharField, Value, Sum, F, Case, When, Exists, Prefetch, Count
from django.db.models.functions import Coalesce, Concat
from django.db.models.fields.files import ImageFieldFile
from django.forms.models import model_to_dict
from django.forms import modelformset_factory

from django_tables2 import RequestConfig

from django.template import RequestContext
from django.template.loader import render_to_string

from datetime import datetime, date
from django.views.generic import ListView

from django.contrib.postgres.search import SearchVector
from decimal import Decimal
from django.db import IntegrityError, transaction

#EMAIL VERIFICATION AND TOKEN
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage

import hashlib
from uuid import uuid4
from rest_framework.authtoken.models import Token

from authentication.filters import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def check_username(request):
    username = request.POST.get('username',None)
    data = {
        'is_taken': UserData.objects.filter(username__iexact=username).exists()
    }

    if data['is_taken']:
        data['error_message'] = 'username sudah digunakan'

    return JsonResponse(data)

def check_email(request):
    email = request.POST.get('email',None)
    data = {
        'is_taken': UserData.objects.filter(email__iexact=email).exists()
    }

    if data['is_taken']:
        data['error_message'] = 'email sudah digunakan'

    return JsonResponse(data)

def check_account_activation(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)

        user_exists = UserData.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).exists()
        if user_exists:
            user = UserData.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()
            group = user.groups.all()[0].name
            is_validate = user.is_validate
            is_active = user.is_active

            if group == 'User' and not is_active:
                is_active = False
            elif group == 'Admin' and is_validate and not is_active:
                is_active = False
            else:
                is_active = True
        else:
            is_active = None

        data = {
            'is_active': is_active
        }

    return JsonResponse(data)

def akses_provinsi(request):
    if request.method == 'POST':
        negara_id = request.POST.get('negara',None)
        data = Provinsi.objects.filter(negara_id = negara_id)

        data_json = serializers.serialize('json', data)
        return HttpResponse(data_json, content_type='application/json')

def akses_dati2(request):
    if request.method == 'POST':
        provinsi_id = request.POST.get('provinsi', None)
        data = Dati2.objects.filter(provinsi_id = provinsi_id)

        data_json = serializers.serialize('json', data)
        return HttpResponse(data_json, content_type='application/json')

def akses_kecamatan(request):
    if request.method == 'POST':
        dati2_id = request.POST.get('dati2', None)
        data = Kecamatan.objects.filter(dati2_id = dati2_id)

        data_json = serializers.serialize('json', data)
        return HttpResponse(data_json, content_type='application/json')

def akses_kelurahan(request):
    if request.method == 'POST':
        kecamatan_id = request.POST.get('kecamatan', None)
        data = Kelurahan.objects.filter(kecamatan_id = kecamatan_id)

        data_json = serializers.serialize('json', data)
        return HttpResponse(data_json, content_type='application/json')

def view_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id',None)
        user = UserData.objects.get(id = user_id)
        admin_profile = UserProfile.objects.get(user_id = user_id)
        token = Token.objects.filter(user_id = user_id).first()

        context = {
                'user':user,
                'admin':admin_profile,
                'token':token,
                }
        template = 'template/views/view_admin.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def set_contact_form(request):
    if request.method == 'POST':
        form_name = request.POST.get('form',None)
        user = request.user
        user_profile = UserProfile.objects.filter(user = user).first()
        user_address = UserAddress.objects.filter(user = user).first()
        form_title = 'Penyesuaian Kontak'
        form_url = reverse("user_update_contact")

        selected_form = UserContactForm(instance=user)
        selected_form.fields['phone_no'].initial = user_profile.phone_no
        selected_form.fields['negara'].initial = user_address.negara
        selected_form.fields['provinsi'].initial = user_address.provinsi
        
        selected_form.fields['dati2'].queryset = Dati2.objects.filter(id = user_address.dati2.id)
        selected_form.fields['dati2'].initial = user_address.dati2
        
        selected_form.fields['kecamatan'].queryset = Kecamatan.objects.filter(id = user_address.kecamatan.id)
        selected_form.fields['kecamatan'].initial = user_address.kecamatan
        
        selected_form.fields['kelurahan'].queryset = Kelurahan.objects.filter(id = user_address.kelurahan.id)
        selected_form.fields['kelurahan'].initial = user_address.kelurahan

        selected_form.fields['address'].initial = user_address.address
        
        data = {
                'form':selected_form,
                }
        template = 'template/forms/tmp_formrow.html'
        html = render_to_string(template_name=template, context=data, request = request, using=None)

        context = {
            'form_title':form_title,
            'form_url':form_url,
            'html':html,
            }
        
        return JsonResponse(context)

def set_description_form(request):
    if request.method == 'POST':
        form_name = request.POST.get('form',None)
        user = request.user
        user_description = UserDescription.objects.filter(user = user).first()
        
        form_title = 'Penyesuaian Deskripsi'
        form_url = reverse("user_update_description")

        selected_form = UserDescriptionForm(instance=user_description)
        
        data = {
                'form':selected_form,
                }
        template = 'template/forms/tmp_formrow.html'
        html = render_to_string(template_name=template, context=data, request = request, using=None)

        context = {
            'form_title':form_title,
            'form_url':form_url,
            'html':html,
            }
        
        return JsonResponse(context)
