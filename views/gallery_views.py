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

#Set Logg
import logging
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
                    status = "LIVE"
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

def gallery_category(request,category):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Gallery']
    title = 'Gallery'

    if category == 'all':
        gallery_query = Gallery.objects.all().order_by('-id')
    elif category == 'photo':
        gallery_query = Gallery.objects.exclude(foto = '').order_by('-id')
    elif category == 'video':
        gallery_query = Gallery.objects.exclude(video = '').order_by('-id')
    elif category == 'link':
        gallery_query = Gallery.objects.filter(link__isnull=False).order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(gallery_query, per_page=9)

    try:
        gallery = paginator.page(page)
    except PageNotAnInteger:
        gallery = paginator.page(1)
    except EmptyPage:
        gallery = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'gallery':gallery,
        'data':category,
        }

    return render(
        request,
        'frontend/gallery/gallery.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def gallery_list(request):
    menu = ['Home','Daftar Galeri']
    title = 'Galeri'
    gallery = Gallery.objects.all().order_by('-id')
    context = {
            'title':title,
            'menu':menu,
            'gallery':gallery
        }

    return render(
        request,
        'backend/gallery/gallery_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def gallery_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Galeri']
    title = 'Tambah Galeri'

    if request.method == 'POST':
        try:
            galleryForm = GalleryForm(request.POST,request.FILES)
            video = request.FILES.get('video',None)
            photo = request.FILES.get('foto',None)
            link = request.POST.get('link',None)

            if (video and photo) or (video and link) or (photo and link):
                messages.add_message(request,messages.ERROR,'Can not upload videos / photos / links at the same time.')
                galleryForm = GalleryForm(request.POST,request.FILES)

                context = {
                    'title':title,
                    'galleryForm':galleryForm
                }
    
                return render(request,'backend/gallery/gallery_form.html',context)
            else:
                if galleryForm.is_valid():
                    item = galleryForm.save()
                    messages.add_message(request,messages.SUCCESS,'Item successfully added to gallery.')

                    return redirect('/gallery/update/edit:'+str(encoding_id(item.id))+'/')
                else: 
                    raise ValidationError('Form tidak lengkap ');
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Error adding item to the gallery.')
            galleryForm = GalleryForm(request.POST,request.FILES)

            context = {
                'title':title,
                'galleryForm':galleryForm
            }
    
            return render(request,'backend/gallery/gallery_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Error adding item to the gallery.')
            galleryForm = GalleryForm(request.POST,request.FILES)

            context = {
                'title':title,
                'galleryForm':galleryForm
            }
    
            return render(request,'backend/gallery/gallery_form.html',context)
    else:
        galleryForm = GalleryForm()

        context = {
            'title':title,
            'galleryForm':galleryForm
        }

        return render(request,'backend/gallery/gallery_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def gallery_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit Galeri']
    title = 'Edit Galeri'
    id = decoding_id(id)
    gallery = Gallery.objects.filter(id=id).first()

    if request.method == 'POST':
        with transaction.atomic():
            galleryForm = GalleryForm(data = request.POST, files = request.FILES, instance=gallery)
            video = request.FILES.get('video',None)
            photo = request.FILES.get('foto',None)
            link = request.POST.get('link',None)
            try:
                if (gallery.video and photo) or (gallery.video and link) or (gallery.foto and video) or (gallery.foto and link) or (gallery.link and video) or (gallery.link and photo):
                    messages.add_message(request,messages.ERROR,'Can not upload videos / photos / links at the same time.')
                    galleryForm = GalleryForm(request.POST,instance=gallery)

                    context = {
                        'title':title,
                        'galleryForm':galleryForm,
                    }
    
                    return render(request,'backend/gallery/gallery_form.html',context)
                else:
                    if galleryForm.is_valid():
                        item = galleryForm.save()
                        messages.add_message(request,messages.SUCCESS,'Item successfully added to gallery.')

                        return redirect('/gallery/update/edit:'+str(encoding_id(item.id))+'/')
                    else:
                        raise forms.ValidationError("Item is invalid.")

            except ValidationError as e:
                messages.add_message(request,messages.ERROR,'Error editing the item.')
                logger.error('Error editing the item '+str(e))
                galleryForm = GalleryForm(request.POST,instance=gallery)

                context = {
                    'title':title,
                    'galleryForm':galleryForm,
                }
    
                return render(request,'backend/gallery/gallery_form.html',context)
            except Exception as e:
                messages.add_message(request,messages.ERROR,'Error editing the item.')
                logger.error('Error editing the item '+str(e))
                galleryForm = GalleryForm(request.POST,instance=gallery)

                context = {
                    'title':title,
                    'galleryForm':galleryForm,
                }
    
                return render(request,'backend/gallery/gallery_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            galleryForm = GalleryForm(instance=gallery)

            context = {
                'title':title,
                'galleryForm':galleryForm,
                }

            return render(request,'backend/gallery/gallery_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Item successfully deleted.')
            gallery.delete()
            return redirect('/gallery/list/')