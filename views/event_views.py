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
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

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

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def list_event(request):
    title = "Event List"

    events = Event.objects.all().order_by('date', 'time')

    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    event_data = []

    for event in events:
        photo = EventPhoto.objects.filter(
            id_event=event
        ).first()

        participant_count = Participant.objects.filter(
            id_event=event
        ).count()

        # default
        status = "EVENT FINISHED"
        badge_class = "badge-completed"
        button_text = "Registration Closed"
        button_class = "btn-secondary"
        can_register = False

        if event.date > today:
            status = "INCOMING"
            badge_class = "badge-upcoming"
            button_text = "Register Now"
            button_class = "btn-primary-custom"
            can_register = True

        elif event.date == today:
            if event.time:
                if event.time.hour == current_time.hour:
                    status = "LIVE MANAGEMENT"
                    badge_class = "badge-active"
                    button_text = "Register Now"
                    button_class = "btn-primary-custom"
                    can_register = True

                elif event.time.hour > current_time.hour:
                    status = "INCOMING"
                    badge_class = "badge-upcoming"
                    button_text = "Register Now"
                    button_class = "btn-primary-custom"
                    can_register = True

        event_data.append({
            "event": event,
            "photo": photo,
            "status": status,
            "badge_class": badge_class,
            "button_text": button_text,
            "button_class": button_class,
            "can_register": can_register,
            "participant_count": participant_count
        })

    paginator = Paginator(event_data, 9)
    page = request.GET.get('page', 1)

    try:
        paginated_events = paginator.page(page)
    except PageNotAnInteger:
        paginated_events = paginator.page(1)
    except EmptyPage:
        paginated_events = paginator.page(paginator.num_pages)

    context = {
        "title": title,
        "events": paginated_events,
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
    title = 'Pengurus'

    team = Team.objects.all().order_by('order','id')

    context = {
                'title':title,
                'team':team,
                }
    return render(request, 'backend/event/doorprize.html',context)

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