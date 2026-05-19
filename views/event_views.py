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

from io import BytesIO
from django.core.files.base import ContentFile

#Set Logg
import logging

from team.models import Team
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
from gallery.models import *
from event.models import *
from participant.models import *
from gallery.forms import *
from form.models import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def list_event(request):
    title = "Event List"

    # =========================================
    # AMBIL PARAMETER FILTER DARI GET
    # =========================================
    q           = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    date_range  = request.GET.get('date_range', '').strip()

    # =========================================
    # BASE QUERYSET
    # =========================================
    events = Event.objects.all().order_by('date', 'time')

    # =========================================
    # FILTER KEYWORD (nama event / lokasi)
    # =========================================
    if q:
        events = events.filter(
            Q(name__icontains=q) |
            Q(location__icontains=q)
        )

    # =========================================
    # FILTER DATE RANGE
    # =========================================
    now          = timezone.localtime()
    today        = now.date()
    current_time = now.time()

    if date_range == 'this_month':
        events = events.filter(
            date__year=today.year,
            date__month=today.month
        )
    elif date_range == 'next_month':
        if today.month == 12:
            next_month = 1
            next_year  = today.year + 1
        else:
            next_month = today.month + 1
            next_year  = today.year

        events = events.filter(
            date__year=next_year,
            date__month=next_month
        )
    elif date_range == 'this_year':
        events = events.filter(date__year=today.year)

    # =========================================
    # BUILD EVENT DATA (dengan status logic)
    # =========================================
    event_data = []

    for event in events:
        photo = EventPhoto.objects.filter(
            id_event=event
        ).first()

        participant_count = Participant.objects.filter(
            id_event=event
        ).count()

        # default
        status      = "EVENT FINISHED"
        badge_class = "badge-completed"
        button_text = "Registration Closed"
        button_class = "btn-secondary"
        can_register = False

        if event.date > today:
            status       = "INCOMING"
            badge_class  = "badge-upcoming"
            button_text  = "Register Now"
            button_class = "btn-primary-custom"
            can_register = True

        elif event.date == today:
            if event.time:
                if event.time.hour == current_time.hour:
                    status       = "LIVE"
                    badge_class  = "badge-active"
                    button_text  = "Register Now"
                    button_class = "btn-primary-custom"
                    can_register = True

                elif event.time.hour > current_time.hour:
                    status       = "INCOMING"
                    badge_class  = "badge-upcoming"
                    button_text  = "Register Now"
                    button_class = "btn-primary-custom"
                    can_register = True

        # =========================================
        # FILTER STATUS (dilakukan setelah kalkulasi)
        # =========================================
        if status_filter:
            if status_filter.upper() != status.upper():
                continue   # skip event yang tidak cocok

        event_data.append({
            "event"            : event,
            "photo"            : photo,
            "status"           : status,
            "badge_class"      : badge_class,
            "button_text"      : button_text,
            "button_class"     : button_class,
            "can_register"     : can_register,
            "participant_count": participant_count
        })

    # =========================================
    # PAGINATION
    # =========================================
    paginator = Paginator(event_data, 9)
    page      = request.GET.get('page', 1)

    try:
        paginated_events = paginator.page(page)
    except PageNotAnInteger:
        paginated_events = paginator.page(1)
    except EmptyPage:
        paginated_events = paginator.page(paginator.num_pages)

    # =========================================
    # CONTEXT
    # =========================================
    context = {
        "title" : title,
        "events": paginated_events,

        # kembalikan nilai filter agar tetap tampil di form
        "filter_q"          : q,
        "filter_status"     : status_filter,
        "filter_date_range" : date_range,
    }

    return render(
        request,
        "frontend/event/list_event.html",
        context
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def participant_upload(request, id):
    event = Event.objects.filter(id=id).first()

    context = {
        "event": event
    }

    return render(
        request,
        'backend/participant/upload_participant.html',
        context
    )


@login_required(login_url='/admin/who-login/')
@admin_only
def doorprize(request):

    assert isinstance(request, HttpRequest)

    title = 'Doorprize'

    # =========================================
    # GET EVENT
    # =========================================

    events = Event.objects.all().order_by(
        '-date',
        '-creation_date'
    )

    selected_event_id = request.GET.get('event')

    selected_event = None

    participants = Participant.objects.none()

    prizes = Doorprize.objects.none()

    winners = DoorprizeWinner.objects.none()

    total_present = 0

    total_winner = 0

    angle_per_segment = 30

    # =========================================
    # IF EVENT SELECTED
    # =========================================

    if selected_event_id:

        selected_event = Event.objects.filter(
            id=selected_event_id
        ).first()

        # =====================================
        # GET WINNER IDS
        # =====================================


        # =====================================
        # PARTICIPANTS PRESENT
        # EXCLUDE WINNERS
        # =====================================

        participants = Participant.objects.select_related(
            'status_user_id',
            'id_event'
        ).filter(
            id_event=selected_event,
            status_user_id__status_name__iexact='Present',
            is_winner = False
        ).order_by(
            'name'
        )

        # =====================================
        # ACTIVE PRIZES
        # =====================================

        prizes = Doorprize.objects.filter(
            id_event=selected_event,
            status='ACTIVE'
        ).order_by(
            'id'
        )

        # =====================================
        # WINNER HISTORY
        # =====================================

        winners = DoorprizeWinner.objects.select_related(
            'id_participant',
            'id_doorprize'
        ).filter(
            id_event=selected_event
        ).order_by(
            '-creation_date'
        )

        # =====================================
        # TOTAL PRESENT
        # =====================================

        total_present = Participant.objects.filter(
            id_event=selected_event,
            status_user_id__status_name__iexact='Present',
            is_winner=False
        ).count()

        # =====================================
        # TOTAL WINNER
        # =====================================

        total_winner = winners.count()

        participant_count = participants.count()

        angle_per_segment = (
            360 / participant_count
            if participant_count > 0
            else 30
        )

    # =========================================
    # CONTEXT
    # =========================================

    context = {

        'title': title,

        'events': events,

        'selected_event': selected_event,

        'participants': participants,

        'prizes': prizes,

        'winners': winners,

        'total_present': total_present,

        'total_winner': total_winner,

        'total_remaining': participants.count(),

        'angle_per_segment': angle_per_segment,

    }

    return render(
        request,
        'backend/event/doorprize.html',
        context
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def team_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Pengurus Form'

    if request.method == 'POST':
        try:
            teamform = TeamForm(request.POST, request.FILES)
            if teamform.is_valid():
                team = teamform.save()
                messages.add_message(request,messages.INFO,''+team.name+' successfully added.')

                return redirect('/team/list/')
            else:
                raise forms.ValidationError("Data is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Team was not added successfully.')
            teamform = TeamForm(request.POST, request.FILES)

            context = {
                'title':title,
                'teamform':teamform,
            }
    
            return render(request,'backend/team/team_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Team was not added successfully.')
            teamform = TeamForm(request.POST, request.FILES)

            context = {
                'title':title,
                'teamform':teamform,
            }
    
            return render(request,'backend/team/team_form.html',context)
    else:
        teamform = TeamForm()

        context = {
            'title':title,
            'teamform':teamform,
            }

        return render(request,'backend/team/team_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def team_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Pengurus'

    id = decoding_id(id)
    
    team = Team.objects.filter(id = id).first()

    if request.method == 'POST':
        try:
            teamform = TeamForm(request.POST, request.FILES, instance=team)

            if teamform.is_valid():
                team_form = teamform.save()
                
                messages.add_message(request,messages.INFO,''+team.name+' successfully edited.')
                return redirect('/team/list/')
            else:
                messages.add_message(request,messages.ERROR,''+news.name+' failed to edit.')

                context = {
                'title':title,
                'newsForm':teamform,
                'picture':'hidden',
                }
    
                return render(request,'backend/team/team_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,''+team.name+' failed to edit (except).')
            teamform = TeamForm(request.POST, request.FILES, instance=team)

            context = {
                'title':title,
                'teamform':teamform,
                'picture':'hidden',
            }
    
            return render(request,'backend/team/team_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            teamform = TeamForm(instance=team)

            context = {
                'title':title,
                'teamform':teamform,
                }

            return render(request,'backend/team/team_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,''+team.name+' successfully deleted.')
            team.delete()
            return redirect('/team/list/')
        
# @login_required(login_url='/admin/who-login/')
# @admin_only
def print_badge(request, id):
    id = decoding_id(id)
    assert isinstance(request, HttpRequest)

    participant = Participant.objects.filter(id = id).first()
    event = Event.objects.filter(id = participant.id_event.id).first()

    instansi = ""

    instansi_obj = FormResponse.objects.annotate(
        instansi=F("data_response__excel_data__Instansi (Jika ada)")
        ).filter(participant_id = id).first()
    if instansi_obj:
        instansi_value = getattr(instansi_obj, 'instansi', '')
        instansi = instansi_value or "Peserta"
        
    if not instansi or instansi.strip().lower() in ["-", "", "tidak ada"]:
        instansi = "Peserta"

    context = {
                'event':event,
                'instansi':instansi,
                'participant':participant,
                }
    return render(request, 'backend/event/badge.html',context)
        
# # @login_required(login_url='/admin/who-login/')
# # @admin_only
# def testing(request):
#     assert isinstance(request, HttpRequest)
#     title = 'Pengurus'

#     event = Event.objects.filter(id = 2).first()
#     participant = Participant.objects.filter(id_event = event)

#     create_and_send_qremail(request,2)

#     for p in participant:
#         if not p.qr_code:
#             qr_data = f"{event.unique_name},{p.unique_user}"

#             # generate QR
#             img = make(qr_data)

#             # convert PIL image to file
#             buffer = BytesIO()
#             img.save(buffer, format='PNG')
#             file_name = f"{event.unique_name}_{p.unique_user}.png"

#             print("filename:", file_name)

#             # save to ImageField
#             p.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)

#             # save model once
#             p.save()

#             print("AFTER SAVE:", p.qr_code.name)

#     url = request.build_absolute_uri(participant.first().qr_code.url)
#     instansi = FormResponse.objects.annotate(
#         instansi=F("data_response__excel_data__Instansi (Jika ada)")
#         ).first()
    
#     current_site = get_current_site(request)

#     context = {
#                 'event': event,
#                 'domain': current_site.domain,
#                 'qr_code': url,
#                 'instansi': instansi.instansi,
#                 'participant':participant.first(),
#                 }
#     return render(request, 'template/registrations/attende_qrcode.html',context)