from django.contrib.auth import password_validation, authenticate, login as user_login, logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages

from django.core import validators,serializers as serial
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.forms import modelformset_factory, formset_factory

from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch
from django.db.models.functions import Coalesce, Concat
from django.db import IntegrityError, transaction, connection

from pathlib import Path
import json
import random
from django.conf import settings
import os
import re
import hashlib
from itertools import chain 

from datetime import datetime, timedelta
from PIL import Image

from django.contrib.postgres.search import SearchVector
from decimal import Decimal
from django.template.loader import render_to_string
from django.template import RequestContext

#EMAIL VERIFICATION AND TOKEN
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.safestring import SafeString

#Test Exception
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from form.models import FormResponse
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

#Set Logg
import logging

from event.forms import EventForm, EventPhotoForm
from participant.models import Participant
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
from banner.models import *
from event.models import *
from banner.forms import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

@login_required(login_url='/admin/who-login/')
@admin_only
def event_list(request, id):
    assert isinstance(request, HttpRequest)

    # ambil event
    event = Event.objects.filter(id=id).first()

    # queryset participant
    participant_queryset = Participant.objects.filter(
        id_event=event
    ).select_related(
        "status_user_id"
    ).order_by("-id")

    # =========================
    # STATISTICS
    # =========================
    total_participants = participant_queryset.count()

    checked_in = participant_queryset.filter(
        status_user_id__status_name__iexact="Present"
    ).count()

    remaining = participant_queryset.filter(
        status_user_id__status_name__iexact="Register"
    ).count()

    attendance_rate = participant_queryset.filter(
        status_user_id__status_name__iexact="Absent"
    ).count()

    # attendance_rate = 0
    # if total_participants > 0:
    #     attendance_rate = round(
    #         (checked_in / total_participants) * 100
    #     )

    form_responses_qs = FormResponse.objects.select_related("participant").filter(
        participant__id_event=event
        ).order_by("-id")

    dynamic_headers = []
    dynamic_rows = []

    base_headers = [
    "name",
    "email",
    "phone",
    "status",
    "qr_code",
    "location",
    ]

    # =========================
    # AMBIL HEADER DARI JSON
    # =========================
    json_headers = []

    for fr in form_responses_qs:
        excel_data = fr.data_response.get("excel_data", {})
        if not json_headers:
            json_headers = list(excel_data.keys())

    # =========================
    # FILTER HEADER JSON (buang yg duplikat participant)
    # =========================
    filtered_json_headers = []

    EXCLUDED_KEYWORDS = [
        "nama", "name", "nama lengkap",
        "email","email address","alamat email",
        "nomor", "phone", "hp", "telp","no hp", "nohandphone",
        "nomor hp", "nomor telepon", "telepon"
        "alamat", "location", "lokasi", "kota","address"
    ]

    for header in json_headers:
        header_clean = str(header).strip().lower()

        # 🔥 TAMBAHAN: skip jika header mengandung keyword tertentu
        if any(keyword in header_clean for keyword in EXCLUDED_KEYWORDS):
            continue

        is_all_same = True

        for fr in form_responses_qs:
            excel_data = fr.data_response.get("excel_data", {})
            val = str(excel_data.get(header, "") or "").strip().lower()

            p = fr.participant

            if val not in [
                str(p.name or "").lower(),
                str(p.email or "").lower(),
                str(p.phone or "").lower(),
                str(p.location or "").lower(),
            ]:
                is_all_same = False
                break

        if not is_all_same:
            filtered_json_headers.append(header)

    # =========================
    # FINAL HEADER (GABUNG)
    # =========================
    final_headers = base_headers + filtered_json_headers

    for fr in form_responses_qs:
        excel_data = fr.data_response.get("excel_data", {})

        # ambil header (hanya sekali)
        if not dynamic_headers:
            dynamic_headers = list(excel_data.keys())

        dynamic_rows.append(excel_data)

    # optional: rename header Timestamp → Waktu Pendaftaran
    clean_headers = []
    for h in dynamic_headers:
        if h.lower() == "timestamp":
            clean_headers.append("Tanggal & Waktu Pendaftaran")
        else:
            clean_headers.append(h)
    # =========================
    # PAGINATION
    # =========================
    page_number = request.GET.get("page", 1)

    paginator = Paginator(
        participant_queryset,
        5  # tampilkan 10 participant per halaman
    )

    participants = paginator.get_page(page_number)

    context = {
        "event": event,
        "participants": participants,
        "total_participants": total_participants,
        "checked_in": checked_in,
        "remaining": remaining,
        "attendance_rate": attendance_rate,

        # 🔥 tambahan
        "dynamic_headers": dynamic_headers,
        "clean_headers": clean_headers,
        "dynamic_rows": dynamic_rows,
        "final_headers": final_headers
    }

    return render(
        request,
        "backend/event/event_list.html",
        context
    )


@login_required(login_url='/admin/who-login/')
@admin_only
def event_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Tambah Event'

    if request.method == 'POST':
        try:
            event_form = EventForm(
                data=request.POST
            )

            photo_form = EventPhotoForm(
                data=request.POST,
                files=request.FILES
            )

            if event_form.is_valid() and photo_form.is_valid():

                # save event terlebih dahulu
                event = event_form.save()

                # save photo jika ada upload
                if request.FILES.get('photo'):
                    event_photo = photo_form.save(commit=False)
                    event_photo.id_event = event
                    event_photo.save()

                messages.success(
                    request,
                    f'Event {event.name} berhasil disimpan.'
                )

                return redirect('/event/list/')

            else:
                raise ValidationError("Data event tidak valid.")

        except ValidationError as e:
            messages.error(
                request,
                'Event gagal disimpan.'
            )

            context = {
                'title': title,
                'event_form': event_form,
                'photo_form': photo_form,
            }

            return render(
                request,
                'backend/event/event_form.html',
                context
            )

        except Exception as e:
            messages.error(
                request,
                'Event gagal disimpan.'
            )

            context = {
                'title': title,
                'event_form': event_form,
                'photo_form': photo_form,
            }

            return render(
                request,
                'backend/event/event_form.html',
                context
            )

    else:
        event_form = EventForm()
        photo_form = EventPhotoForm()

        context = {
            'title': title,
            'event_form': event_form,
            'photo_form': photo_form,
        }

        return render(
            request,
            'backend/event/event_form.html',
            context
        )

@login_required(login_url='/admin/who-login/')
@admin_only
def event_update(request, status, id):
    id = decoding_id(id)
    if not id:
        return redirect('/')

    assert isinstance(request, HttpRequest)
    title = 'Perbarui Banner'
    
    banner = Banner.objects.get_by_id(id = id)

    if request.method == 'POST':
        try:
            bannerForm = BannerForm(data = request.POST, files = request.FILES, instance=banner)
            is_active = request.POST.get('is_active',None)
            if bannerForm.is_valid():
                banner = bannerForm.save(commit=False)
                banner.is_active = is_active
                banner.save()

                messages.add_message(request,messages.INFO,'Banner '+banner.title+' successfuly saved.')
                return redirect('/banner/list/')
            else:
                messages.add_message(request,messages.ERROR,'Banner '+banner.title+' not successfuly saved.')

                context = {
                'title':title,
                'form':bannerForm,
                   }
    
                return render(request,'backend/banner/banner_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Banner '+banner.name+' not successfuly saved.')
            bannerForm = BannerForm(request.POST, request.FILES, instance=banner)

            context = {
                'title':title,
                'form':bannerForm,
            }
    
            return render(request,'backend/banner/banner_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            bannerForm = BannerForm(instance=banner)
            if banner.is_active == True:
                bannerForm.fields['is_active'].initial = 1
            else:
                bannerForm.fields['is_active'].initial = 0

            context = {
                'title':title,
                'form':bannerForm,
                }

            return render(request,'backend/banner/banner_form.html',context)
        elif status == 'delete':
            banner = Banner.objects.get_by_id(id = id)
            messages.add_message(request,messages.WARNING,'Banner '+banner.title+' successfuly deleted.')
            banner.delete()
            return redirect('/banner/list/')




@login_required(login_url='/admin/who-login/')
@admin_only
def banner_list(request):
    assert isinstance(request, HttpRequest)
    title = 'List Banner'
    banner = Banner.objects.all().order_by('title')

    context = {'title':title,
               'banner':banner,}
    return render(request, 'backend/banner/banner_list.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def banner_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Tambah Banner'

    if request.method == 'POST':
        try:
            is_active = request.POST.get('is_active',None)
            bannerForm = BannerForm(data = request.POST, files = request.FILES)
            if bannerForm.is_valid():
                banner = bannerForm.save(commit=False)
                banner.is_active = is_active
                banner.save()
                
                messages.add_message(request,messages.INFO,'Banner '+banner.title+' is saved.')

                return redirect('/banner/list/')
            else:
                raise forms.ValidationError("Data banner tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Banner failed to save.')
            bannerForm = BannerForm(request.POST, request.FILES)

            context = {
                'title':title,
                'form':bannerForm,
            }
    
            return render(request,'backend/banner/banner_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Banner failed to save.')
            bannerForm = BannerForm(request.POST, request.FILES)

            context = {
                'title':title,
                'form':bannerForm,
            }
    
            return render(request,'backend/banner/banner_form.html',context)
    else:
        bannerForm = BannerForm()

        context = {
            'title':title,
            'form':bannerForm,
            }

        return render(request,'backend/banner/banner_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def banner_update(request, status, id):
    id = decoding_id(id)
    if not id:
        return redirect('/')

    assert isinstance(request, HttpRequest)
    title = 'Perbarui Banner'
    
    banner = Banner.objects.get_by_id(id = id)

    if request.method == 'POST':
        try:
            bannerForm = BannerForm(data = request.POST, files = request.FILES, instance=banner)
            is_active = request.POST.get('is_active',None)
            if bannerForm.is_valid():
                banner = bannerForm.save(commit=False)
                banner.is_active = is_active
                banner.save()

                messages.add_message(request,messages.INFO,'Banner '+banner.title+' successfuly saved.')
                return redirect('/banner/list/')
            else:
                messages.add_message(request,messages.ERROR,'Banner '+banner.title+' not successfuly saved.')

                context = {
                'title':title,
                'form':bannerForm,
                   }
    
                return render(request,'backend/banner/banner_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Banner '+banner.name+' not successfuly saved.')
            bannerForm = BannerForm(request.POST, request.FILES, instance=banner)

            context = {
                'title':title,
                'form':bannerForm,
            }
    
            return render(request,'backend/banner/banner_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            bannerForm = BannerForm(instance=banner)
            if banner.is_active == True:
                bannerForm.fields['is_active'].initial = 1
            else:
                bannerForm.fields['is_active'].initial = 0

            context = {
                'title':title,
                'form':bannerForm,
                }

            return render(request,'backend/banner/banner_form.html',context)
        elif status == 'delete':
            banner = Banner.objects.get_by_id(id = id)
            messages.add_message(request,messages.WARNING,'Banner '+banner.title+' successfuly deleted.')
            banner.delete()
            return redirect('/banner/list/')
        



