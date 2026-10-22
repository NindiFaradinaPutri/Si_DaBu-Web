"""
Definition of views.
"""

import base64
from io import BytesIO
from django.urls import reverse
from django.contrib.auth import password_validation, authenticate, login as user_login, logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from form.models import (
    Form,
    FormQuestion,
    FormQuestionOption
)



from django.core import validators,serializers as serial
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.core.files.storage import FileSystemStorage, default_storage

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.forms import modelformset_factory, formset_factory

from django.db.models import Q, CharField, IntegerField, Value, Sum, F, Case, When, Exists, Prefetch
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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.safestring import SafeString

#Test Exception
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import qrcode
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

from banner.models import Banner
from event.models import *
from participant.models import Participant
<<<<<<< HEAD
# from team.models import *
# from team.forms import *
=======
from team.models import *
from team.forms import *
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609

from profile.models import *
from portfolio.models import *

<<<<<<< HEAD
# from information.models import *
=======
from information.models import *
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609

#Set Logg
import logging
logger = logging.getLogger(__file__)

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def handler400(request, *args, **argv):
    return render(request,'error_handler/400.html', status=400)

def handler403(request, *args, **argv):
    return render(request,'error_handler/403.html', status=403)

def handler404(request, *args, **argv):
    return render(request,'error_handler/404.html', status=404)

def handler500(request, *args, **argv):
    return render(request,'error_handler/500.html', status=500)

def csrf_failure(request, reason=""):
    return render(request,'error_handler/403_csrf.html', status=403)


# def home(request):
#     kegiatans = KegiatanMasjid.objects.all().order_by('id')
#     client = Client.objects.all()
#     profile = Profile.objects.filter(id=1).first()

#     # semua event
#     now = timezone.localtime()

#     today = now.date()
#     current_time = now.time()

#     events = Event.objects.all().annotate(

#         event_priority=Case(

#             # upcoming event
#             When(date__gt=today, then=Value(0)),

#             # hari ini tapi belum lewat
#             When(
#                 date=today,
#                 time__gte=current_time,
#                 then=Value(0)
#             ),

#             # event lama
#             default=Value(1),

#             output_field=IntegerField()
#         )

#     ).order_by(

#         # upcoming dulu
#         'event_priority',

#         # urut terdekat
#         'date',
#         'time'
#     )

#     now = timezone.localtime()
#     today = now.date()
#     current_time = now.time()

#     # ======================================
#     # HERO SECTION (ambil event terdekat)
#     # ======================================
#     hero_event = events.first()

#     hero_event_photo = None
#     hero_event_status = None
#     hero_maps_url = ""
#     hero_badge_class = "hero-badge"

#     if hero_event:
        
#         hero_maps_url = extract_maps_url(hero_event.location_map)
#         hero_participant_count = Participant.objects.filter(
#             id_event=hero_event
#         ).count()

#         hero_event_photo = EventPhoto.objects.filter(
#             id_event=hero_event
#         ).first()

#         event_date = hero_event.date
#         event_time = hero_event.time

#         if event_date == today:
#             if event_time:
#                 if event_time.hour == current_time.hour:
#                     hero_event_status = "LIVE"
#                     hero_badge_class = "hero-badge bg-danger text-white"

#                 elif event_time.hour > current_time.hour:
#                     hero_event_status = "INCOMING"
#                     hero_badge_class = "hero-badge bg-warning text-dark"

#                 else:
#                     hero_event_status = "EVENT FINISHED"
#                     hero_badge_class = "hero-badge bg-secondary text-white"
#             else:
#                 hero_event_status = "LIVE"
#                 hero_badge_class = "hero-badge bg-danger text-white"

#         elif event_date > today:
#             hero_event_status = "INCOMING"
#             hero_badge_class = "hero-badge bg-warning text-dark"

#         else:
#             hero_event_status = "EVENT FINISHED"
#             hero_badge_class = "hero-badge bg-secondary text-white"

#     # ======================================
#     # EVENT CARD LIST
#     # ======================================
#     event_data = []

#     for event in events:
#         photo = EventPhoto.objects.filter(
#             id_event=event
#         ).first()

#         # default
#         status = "EVENT FINISHED"
#         badge_class = "bg-secondary text-white"

#         if event.date > today:
#             status = "INCOMING"
#             badge_class = "bg-warning text-dark"

#         elif event.date == today:
#             if event.time:
#                 if event.time.hour == current_time.hour:
#                     status = "LIVE"
#                     badge_class = "bg-danger text-white"

#                 elif event.time.hour > current_time.hour:
#                     status = "INCOMING"
#                     badge_class = "bg-warning text-dark"

#                 else:
#                     status = "EVENT FINISHED"
#                     badge_class = "bg-secondary text-white"
#             else:
#                 status = "LIVE"
#                 badge_class = "bg-danger text-white"

#         event_data.append({
#             "event": event,
#             "photo": photo,
#             "status": status,
#             "badge_class": badge_class,
#             "maps_url": extract_maps_url(event.location_map)
#         })

#     context = {
#         'title': 'Halaman Beranda',
#         'kegiatans': kegiatans,
#         'client': client,
#         'profile': profile,

#         # hero section
#         'event': hero_event,
#         'event_photo': hero_event_photo,
#         'event_status': hero_event_status,
#         'badge_class': hero_badge_class,
#         'hero_participant_count': hero_participant_count,

#         # event list section
#         'event_data': event_data,
#         'hero_maps_url': hero_maps_url,  #  tambahan
#     }

#     return render(
#         request,
#         'frontend/home/index.html',
#         context
#     )

def home(request):

<<<<<<< HEAD
   
=======
    kegiatans = KegiatanMasjid.objects.all().order_by('id')
    client = Client.objects.all()
    profile = Profile.objects.filter(id=1).first()

    now = timezone.localtime()

    today = now.date()
    current_time = now.time()

    # ======================================
    # HERO EVENT PRIORITY
    # ======================================
    all_events = Event.objects.all().annotate(

        event_priority=Case(

            # upcoming event
            When(
                date__gt=today,
                then=Value(0)
            ),

            # today but not finished
            When(
                date=today,
                time__gte=current_time,
                then=Value(0)
            ),

            # finished event
            default=Value(1),

            output_field=IntegerField()
        )

    ).order_by(
        'event_priority',
        'date',
        'time'
    )

    # ======================================
    # HERO EVENT
    # ======================================
    hero_event = all_events.first()

    hero_event_photo = None
    hero_event_status = None
    hero_maps_url = ""
    hero_badge_class = "hero-badge"

    hero_participant_count = 0

    if hero_event:

        hero_maps_url = extract_maps_url(
            hero_event.location_map
        )

        hero_participant_count = Participant.objects.filter(
            id_event=hero_event
        ).count()

        hero_event_photo = EventPhoto.objects.filter(
            id_event=hero_event
        ).first()

        event_date = hero_event.date
        event_time = hero_event.time

        if event_date > today:

            hero_event_status = "INCOMING"
            hero_badge_class = "hero-badge bg-warning text-dark"

        elif event_date == today:

            if event_time:

                if event_time.hour == current_time.hour:

                    hero_event_status = "LIVE"
                    hero_badge_class = "hero-badge bg-danger text-white"

                elif event_time.hour > current_time.hour:

                    hero_event_status = "INCOMING"
                    hero_badge_class = "hero-badge bg-warning text-dark"

                else:

                    hero_event_status = "EVENT FINISHED"
                    hero_badge_class = "hero-badge bg-secondary text-white"

            else:

                hero_event_status = "LIVE"
                hero_badge_class = "hero-badge bg-danger text-white"

        else:

            hero_event_status = "EVENT FINISHED"
            hero_badge_class = "hero-badge bg-secondary text-white"

    # ======================================
    # UPCOMING EVENTS
    # ======================================
    upcoming_events = Event.objects.filter(

        Q(date__gt=today) |

        Q(
            date=today,
            time__gte=current_time
        )

    ).order_by(
        'date',
        'time'
    )[:6]

    # ======================================
    # FINISHED EVENTS
    # ======================================
    finished_events = Event.objects.filter(

        Q(date__lt=today) |

        Q(
            date=today,
            time__lt=current_time
        )

    ).order_by(
        '-date',
        '-time'
    )[:6]

    # ======================================
    # BUILD EVENT DATA
    # ======================================
    def build_event_data(events_queryset):

        data = []

        for event in events_queryset:

            photo = EventPhoto.objects.filter(
                id_event=event
            ).first()

            # default
            status = "EVENT FINISHED"
            badge_class = "bg-secondary text-white"

            if event.date > today:

                status = "INCOMING"
                badge_class = "bg-warning text-dark"

            elif event.date == today:

                if event.time:

                    if event.time.hour == current_time.hour:

                        status = "LIVE"
                        badge_class = "bg-danger text-white"

                    elif event.time.hour > current_time.hour:

                        status = "INCOMING"
                        badge_class = "bg-warning text-dark"

                    else:

                        status = "EVENT FINISHED"
                        badge_class = "bg-secondary text-white"

                else:

                    status = "LIVE"
                    badge_class = "bg-danger text-white"

            data.append({

                "event": event,
                "photo": photo,
                "status": status,
                "badge_class": badge_class,
                "maps_url": extract_maps_url(
                    event.location_map
                )

            })

        return data

    # ======================================
    # FINAL DATA
    # ======================================
    upcoming_event_data = build_event_data(
        upcoming_events
    )

    finished_event_data = build_event_data(
        finished_events
    )
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609

    context = {

        'title': 'Halaman Beranda',

<<<<<<< HEAD
       
=======
        'kegiatans': kegiatans,
        'client': client,
        'profile': profile,

        # hero
        'event': hero_event,
        'event_photo': hero_event_photo,
        'event_status': hero_event_status,
        'badge_class': hero_badge_class,
        'hero_participant_count': hero_participant_count,
        'hero_maps_url': hero_maps_url,

        # sections
        'upcoming_event_data': upcoming_event_data,
        'finished_event_data': finished_event_data,
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609
    }

    return render(
        request,
        'frontend/home/index.html',
        context
    )


def event_frontend(request, id):
    menu = ['Beranda', 'Detail Event']

    profile = Profile.objects.filter(id=1).first()
    contact = Contact.objects.filter(id=1).first()
    client = Client.objects.all()
    tech = Technology.objects.all()
    naration = TeamNaration.objects.filter(id=1).first()

    id = decoding_id(id)

    # ambil event
    event = Event.objects.filter(id=id).first()



    # ambil photo event
    event_photo = EventPhoto.objects.filter(
        id_event=event
    ).first()

    event_benefits = EventBenefit.objects.filter(
    id_event=event,
    status=True
    ).order_by('id')

    # participant count
    participant_count = Participant.objects.filter(
        id_event=event
    ).count()

    # =========================
    # EVENT STATUS LOGIC
    # =========================
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    event_status = "EVENT FINISHED"
    event_badge_class = "bg-secondary text-white"

    if event.date > today:
        event_status = "INCOMING"
        event_badge_class = "bg-warning text-dark"

    elif event.date == today:
        if event.time:
            if event.time.hour == current_time.hour:
                event_status = "LIVE"
                event_badge_class = "bg-danger text-white"

            elif event.time.hour > current_time.hour:
                event_status = "INCOMING"
                event_badge_class = "bg-warning text-dark"

            else:
                event_status = "EVENT FINISHED"
                event_badge_class = "bg-secondary text-white"
        else:
            event_status = "LIVE"
            event_badge_class = "bg-danger text-white"

    # =========================
    # Attendance Progress
    # =========================
    max_capacity = 5000

    if participant_count > 0:
        progress_percentage = min(
            round((participant_count / max_capacity) * 100),
            100
        )
    else:
        progress_percentage = 0

    # =========================
    # Generate QR Code jika pakai Google Form
    # =========================
    qr_code_base64 = None

    if event.is_form and event.url_form:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )

        qr.add_data(event.url_form)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")

        qr_code_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode()

    # =========================
    # DYNAMIC FORM
    # =========================
    form_event = Form.objects.filter(
        id_event=event,
        status=True
    ).first()

    form_questions = []

    if form_event:
        form_questions = FormQuestion.objects.filter(
            id_form=form_event
        ).prefetch_related(
            'formquestionoption_set'
        ).order_by('order')

        if request.method == "POST" and not event.is_form:

            response_data = {}
            form_json = {}

            participant_name = ""
            participant_email = ""
            participant_phone = ""
            participant_location = ""

            # =========================
            # VALIDASI REQUIRED
            # =========================
            for question in form_questions:

                field_name = f"question_{question.id}"

                # MULTIPLE CHOICE
                if question.type == "multiple_choice":
                    value = request.POST.getlist(field_name)

                # FILE / IMAGE
                elif question.type in ['file_upload', 'image_upload']:
                    value = request.FILES.get(field_name)

                else:
                    value = request.POST.get(field_name)

                # REQUIRED VALIDATION
                if question.form_required:

                    is_empty = False

                    if question.type == "multiple_choice":
                        is_empty = len(value) == 0

                    elif question.type in ['file_upload', 'image_upload']:
                        is_empty = value is None

                    else:
                        is_empty = not value

                    if is_empty:

                        messages.error(
                            request,
                            f"{question.label} wajib diisi."
                        )

                        return redirect(request.path)

            # =========================
            # BUILD RESPONSE DATA
            # =========================
            for question in form_questions:

                field_name = f"question_{question.id}"

                # MULTIPLE CHOICE
                if question.type == "multiple_choice":

                    value = request.POST.getlist(field_name)

                # FILE / IMAGE
                elif question.type in ['file_upload', 'image_upload']:

                    file = request.FILES.get(field_name)

                    if file:

                        # simpan file
                        upload_path = f"event/{file.name}"

                        saved_path = default_storage.save(
                            upload_path,
                            ContentFile(file.read())
                        )

                        # format path
                        value = f"/static/media/{saved_path}"

                    else:
                        value = ""

                else:

                    value = request.POST.get(field_name)

                # =========================
                # JSON FORM RESPONSE
                # =========================
                response_data[str(question.id)] = {
                    "question": question.label,
                    "type": question.type,
                    "value": value
                }

                # format mirip excel upload
                clean_label = re.sub(
                    r"^\d+\.\s*",
                    "",
                    re.sub(
                        r"\s+",
                        " ",
                        str(question.label).replace(":", "").strip()
                    )
                )

                # format mirip excel upload
                form_json[clean_label] = value

                # =========================
                # AUTO MAPPING PARTICIPANT
                # =========================
                label_lower = question.label.lower().strip()

                # NAME
                if (
                    "name" in label_lower or
                    "nama" in label_lower
                ):
                    participant_name = value

                # EMAIL
                elif (
                    question.type == "email" or
                    "email" in label_lower or
                    "alamatemail" in label_lower or
                    "emailaddress" in label_lower
                ):
                    participant_email = value

                # PHONE
                elif (
                    question.type == "phone" or
                    "phone" in label_lower or
                    "hp" in label_lower or
                    "telepon" in label_lower or
                    "nomor" in label_lower
                ):
                    participant_phone = value

                # LOCATION
                elif (
                    "location" in label_lower or
                    "alamat" in label_lower or
                    "kota" in label_lower or
                    "address" in label_lower
                ):
                    participant_location = value

            # fallback name
            if not participant_name:
                participant_name = "Guest Participant"

            # =========================
            # STATUS REGISTER
            # =========================
            status_register = StatusParticipant.objects.filter(
                status_name__iexact="Register"
            ).first()

            if not status_register:

                status_register = StatusParticipant.objects.create(
                    status_name="Register",
                    information="Participant Registered"
                )

            # =========================
            # CHECK EXISTING PARTICIPANT
            # =========================
            participant = Participant.objects.filter(
                name__iexact=participant_name,
                phone=participant_phone,
                id_event=event
            ).first()

            # =========================
            # UPDATE EXISTING
            # =========================
            if participant:

                participant.name = participant_name
                participant.email = participant_email
                participant.phone = participant_phone
                participant.location = participant_location
                participant.status_user_id = status_register
                participant.save()

            # =========================
            # CREATE NEW PARTICIPANT
            # =========================
            else:

                participant = Participant.objects.create(
                    name=participant_name,
                    email=participant_email,
                    phone=participant_phone,
                    location=participant_location,
                    status_user_id=status_register,
                    id_event=event
                )

            # =========================
            # SAVE FORM RESPONSE
            # =========================
            response_json = {
                "participant_id": participant.id,
                "participant_name": participant.name,
                "participant_email": participant.email,
                "participant_phone": participant.phone,
                "excel_data": form_json
            }

            FormResponse.objects.create(
                form=form_event,
                participant=participant,
                data_response=response_json
            )

            messages.success(
                request,
                "Registration berhasil dikirim."
            )
            # =========================
            # GENERATE QR + SEND EMAIL
            # =========================
            create_and_send_qremail(
                request,
                event.id
            )


            return redirect(request.path)

    context = {
        'title': event.name,
        'menu': menu,
        'profile': profile,
        'contact': contact,
        'client': client,
        'tech': tech,
        'naration': naration,

        # event
        'event': event,
        'event_photo': event_photo,
        'event_benefits': event_benefits,

        # participant
        'participant_count': participant_count,
        'max_capacity': max_capacity,
        'progress_percentage': progress_percentage,

        # status
        'event_status': event_status,
        'event_badge_class': event_badge_class,

        # qr
        'qr_code_base64': qr_code_base64,

        # dynamic form
        'form_event': form_event,
        'form_questions': form_questions,
    }

    return render(
        request,
        'frontend/event/event.html',
        context,
    )

def ourteam(request):
    menu = ['Home','DKM Masjid Ar-Raudah']

    team = Team.objects.all().order_by('order','id')
    naration = TeamNaration.objects.filter(id = 1).first()

    context = {
            'title':'DKM Masjid Ar-Raudah',
            'menu':menu,
            'team':team,
            'naration':naration
        }

    return render(
        request,
        'frontend/team/team.html',
        context,
    )

