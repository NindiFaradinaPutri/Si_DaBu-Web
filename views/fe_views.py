"""
Definition of views.
"""

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

from django.shortcuts import get_object_or_404, render, redirect
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
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

from banner.models import Banner
from event.models import *
from participant.models import Participant
from team.models import *
from team.forms import *

from profile.models import *
from portfolio.models import *

from information.models import *

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


def home(request):
    kegiatans = KegiatanMasjid.objects.all().order_by('id')
    client = Client.objects.all()
    profile = Profile.objects.filter(id=1).first()

    # semua event
    events = Event.objects.all().order_by('date', 'time')

    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # ======================================
    # HERO SECTION (ambil event terdekat)
    # ======================================
    hero_event = events.first()

    hero_event_photo = None
    hero_event_status = None
    hero_badge_class = "hero-badge"

    if hero_event:

        hero_participant_count = Participant.objects.filter(
            id_event=hero_event
        ).count()

        hero_event_photo = EventPhoto.objects.filter(
            id_event=hero_event
        ).first()

        event_date = hero_event.date
        event_time = hero_event.time

        if event_date == today:
            if event_time:
                if event_time.hour == current_time.hour:
                    hero_event_status = "LIVE MANAGEMENT"
                    hero_badge_class = "hero-badge bg-danger text-white"

                elif event_time.hour > current_time.hour:
                    hero_event_status = "INCOMING"
                    hero_badge_class = "hero-badge bg-warning text-dark"

                else:
                    hero_event_status = "EVENT FINISHED"
                    hero_badge_class = "hero-badge bg-secondary text-white"
            else:
                hero_event_status = "LIVE MANAGEMENT"
                hero_badge_class = "hero-badge bg-danger text-white"

        elif event_date > today:
            hero_event_status = "INCOMING"
            hero_badge_class = "hero-badge bg-warning text-dark"

        else:
            hero_event_status = "EVENT FINISHED"
            hero_badge_class = "hero-badge bg-secondary text-white"

    # ======================================
    # EVENT CARD LIST
    # ======================================
    event_data = []

    for event in events:
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
                    status = "LIVE MANAGEMENT"
                    badge_class = "bg-danger text-white"

                elif event.time.hour > current_time.hour:
                    status = "INCOMING"
                    badge_class = "bg-warning text-dark"

                else:
                    status = "EVENT FINISHED"
                    badge_class = "bg-secondary text-white"
            else:
                status = "LIVE MANAGEMENT"
                badge_class = "bg-danger text-white"

        event_data.append({
            "event": event,
            "photo": photo,
            "status": status,
            "badge_class": badge_class
        })

    context = {
        'title': 'Halaman Beranda',
        'kegiatans': kegiatans,
        'client': client,
        'profile': profile,

        # hero section
        'event': hero_event,
        'event_photo': hero_event_photo,
        'event_status': hero_event_status,
        'badge_class': hero_badge_class,
        'hero_participant_count': hero_participant_count,

        # event list section
        'event_data': event_data,
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

    # ambil event berdasarkan ID
    event = Event.objects.filter(id=id).first()

    # ambil photo event
    event_photo = EventPhoto.objects.filter(
        id_event=event
    ).first()

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
                event_status = "LIVE MANAGEMENT"
                event_badge_class = "bg-danger text-white"

            elif event.time.hour > current_time.hour:
                event_status = "INCOMING"
                event_badge_class = "bg-warning text-dark"

            else:
                event_status = "EVENT FINISHED"
                event_badge_class = "bg-secondary text-white"
        else:
            event_status = "LIVE MANAGEMENT"
            event_badge_class = "bg-danger text-white"

    # kapasitas
    max_capacity = 5000

    if participant_count > 0:
        progress_percentage = min(
            round((participant_count / max_capacity) * 100),
            100
        )
    else:
        progress_percentage = 0

    context = {
        'title': event.name,
        'menu': menu,
        'profile': profile,
        'contact': contact,
        'client': client,
        'tech': tech,
        'naration': naration,

        'event': event,
        'event_photo': event_photo,
        'participant_count': participant_count,
        'max_capacity': max_capacity,
        'progress_percentage': progress_percentage,

        # status
        'event_status': event_status,
        'event_badge_class': event_badge_class,
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

