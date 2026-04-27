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
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
from career.models import *
from career.forms import *
from team.models import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def career(request):
    assert isinstance(request, HttpRequest)
    menu = ['Beranda','Keuangan']
    title = 'Keuangan'

    career_query = Career.objects.all().order_by('position')

    page = request.GET.get('page',1)

    paginator = Paginator(career_query, per_page=10)

    try:
        career = paginator.page(page)
    except PageNotAnInteger:
        career = paginator.page(1)
    except EmptyPage:
        career = paginator.page(paginator.num_pages)

    career_detail = CareerDetail.objects.all()
    career_photo = CareerPhoto.objects.all()
    naration = TeamNaration.objects.all()

    context = {
        'title':title,
        'menu':menu,
        'career':career,
        'career_detail':career_detail,
        'career_photo':career_photo,
        'naration':naration
        }

    return render(
        request,
        'frontend/career/career.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def career_list(request):
    menu = ['Home','Career List']
    title = 'Career List'
    career = Career.objects.all().order_by('position')
    context = {
            'title':title,
            'menu':menu,
            'career':career
        }

    return render(
        request,
        'backend/career/career_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def career_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add New Position'

    if request.method == 'POST':
        try:
            careerForm = CareerForm(data = request.POST)
            if careerForm.is_valid():
                career = careerForm.save()
                
                messages.add_message(request,messages.INFO,career.position +' position successfully added.')

                return redirect('/career/update/edit:'+str(encoding_id(career.id)))
            else:
                raise forms.ValidationError("Position is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Position was not added successfully.')
            careerForm = CareerForm(request.POST)

            context = {
                'title':title,
                'careerForm':careerForm,
            }
    
            return render(request,'backend/career/career_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Position was not added successfully.')
            careerForm = CareerForm(request.POST)

            context = {
                'title':title,
                'careerForm':careerForm,
            }
    
            return render(request,'backend/career/career_form.html',context)
    else:
        careerForm = CareerForm()

        context = {
            'title':title,
            'careerForm':careerForm,
            }

        return render(request,'backend/career/career_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def career_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Position'

    id = decoding_id(id)
    
    career = Career.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            careerForm = CareerForm(data = request.POST, instance=career)

            if careerForm.is_valid():
                career = careerForm.save()
                
                messages.add_message(request,messages.INFO,career.position +' position successfully edited.')
                return redirect('/career/update/edit:'+str(encoding_id(career.id)))
            else:
                messages.add_message(request,messages.ERROR,career.name +' position failed to edit (else).')

                context = {
                'title':title,
                'careerForm':careerForm,
                }
    
                return render(request,'backend/career/career_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,career.name +' position failed to edit (except).')
            careerForm = CareerForm(request.POST, instance=career)

            context = {
                'title':title,
                'careerForm':careerForm,
            }
    
            return render(request,'backend/career/career_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            careerForm = CareerForm(instance=career)

            context = {
                'title':title,
                'careerForm':careerForm,
                }

            return render(request,'backend/career/career_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,career.position+' position successfully deleted.')
            career.delete()
            return redirect('/career/list/')

@login_required(login_url='/admin/who-login/')
@admin_only
def career_photo_list(request):
    menu = ['Home','Career Photo List']
    title = 'Career Photo List'
    career_photo = CareerPhoto.objects.all().order_by('id')
    context = {
            'title':title,
            'menu':menu,
            'career_photo':career_photo
        }

    return render(
        request,
        'backend/career/career_photo_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def career_photo_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add New Photo'

    if request.method == 'POST':
        try:
            careerPhotoForm = CareerPhotoForm(data = request.POST, files = request.FILES)
            if careerPhotoForm.is_valid():
                career_photo = careerPhotoForm.save()
                
                messages.add_message(request,messages.INFO,'Successfully upload the photo.')

                return redirect('/career/photo/edit:'+str(encoding_id(career_photo.id)))
            else:
                raise forms.ValidationError("Photo is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Photo was not added successfully.')
            careerPhotoForm = CareerPhotoForm(data = request.POST, files = request.FILES)

            context = {
                'title':title,
                'careerPhotoForm':careerPhotoForm,
            }
    
            return render(request,'backend/career/career_photo_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Photo was not added successfully.')
            careerPhotoForm = CareerPhotoForm(data = request.POST, files = request.FILES)

            context = {
                'title':title,
                'careerPhotoForm':careerPhotoForm,
            }
    
            return render(request,'backend/career/career_photo_form.html',context)
    else:
        careerPhotoForm = CareerPhotoForm()

        context = {
            'title':title,
            'careerPhotoForm':careerPhotoForm,
            }

        return render(request,'backend/career/career_photo_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def career_photo_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Photo'

    id = decoding_id(id)
    
    career_photo = CareerPhoto.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            careerPhotoForm = CareerPhotoForm(data = request.POST, files = request.FILES, instance=career_photo)

            if careerPhotoForm.is_valid():
                career_photo = careerPhotoForm.save()
                
                messages.add_message(request,messages.INFO,'The photo successfully edited.')
                return redirect('/career/photo/edit:'+str(encoding_id(career_photo.id)))
            else:
                messages.add_message(request,messages.ERROR,'Failed to edit the photo (else).')

                context = {
                'title':title,
                'careerPhotoForm':careerPhotoForm,
                }
    
                return render(request,'backend/career/career_photo_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,career.name +' position failed to edit (except).')
            careerPhotoForm = CareerPhotoForm(request.POST, request.FILES, instance=career_photo)

            context = {
                'title':title,
                'careerPhotoForm':careerPhotoForm,
            }
    
            return render(request,'backend/career/career_photo_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            careerPhotoForm = CareerPhotoForm(instance=career_photo)

            context = {
                'title':title,
                'careerPhotoForm':careerPhotoForm,
                }

            return render(request,'backend/career/career_photo_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Successfully deleted the photo.')
            career_photo.delete()
            return redirect('/career/photo/list/')

@login_required(login_url='/admin/who-login/')
@admin_only
def career_detail_list(request):
    menu = ['Home','Career Detail List']
    title = 'Career Detail List'
    career_detail = CareerDetail.objects.all().order_by('id')
    context = {
            'title':title,
            'menu':menu,
            'career_detail':career_detail
        }

    return render(
        request,
        'backend/career/career_detail_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def career_detail_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add New Detail'

    if request.method == 'POST':
        try:
            careerDetailForm = CareerDetailForm(data = request.POST)
            if careerDetailForm.is_valid():
                career_detail = careerDetailForm.save()
                
                messages.add_message(request,messages.INFO,career_detail.title +' detail successfully added.')

                return redirect('/career/detail/edit:'+str(encoding_id(career_detail.id)))
            else:
                raise forms.ValidationError("Position is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Detail was not added successfully.')
            careerDetailForm = CareerDetailForm(request.POST)

            context = {
                'title':title,
                'careerDetailForm':careerDetailForm,
            }
    
            return render(request,'backend/career/career_detail_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Detail was not added successfully.')
            careerDetailForm = CareerDetailForm(request.POST)

            context = {
                'title':title,
                'careerDetailForm':careerDetailForm,
            }
    
            return render(request,'backend/career/career_detail_form.html',context)
    else:
        careerDetailForm = CareerDetailForm()

        context = {
            'title':title,
            'careerDetailForm':careerDetailForm,
            }

        return render(request,'backend/career/career_detail_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def career_detail_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Detail'

    id = decoding_id(id)
    
    career_detail = CareerDetail.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            careerDetailForm = CareerDetailForm(data = request.POST, instance=career_detail)

            if careerDetailForm.is_valid():
                career_detail = careerDetailForm.save()
                
                messages.add_message(request,messages.INFO,career_detail.title +' detail successfully edited.')
                return redirect('/career/detail/edit:'+str(encoding_id(career_detail.id)))
            else:
                messages.add_message(request,messages.ERROR,career_detail.title +' detail failed to edit (else).')

                context = {
                'title':title,
                'careerDetailForm':careerDetailForm,
                }
    
                return render(request,'backend/career/career_detail_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,career_detail.title +' position failed to edit (except).')
            careerDetailForm = CareerDetailForm(request.POST, instance=career_detail)

            context = {
                'title':title,
                'careerDetailForm':careerDetailForm,
            }
    
            return render(request,'backend/career/career_detail_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            careerDetailForm = CareerDetailForm(instance=career_detail)

            context = {
                'title':title,
                'careerDetailForm':careerDetailForm,
                }

            return render(request,'backend/career/career_detail_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,career_detail.title+' detail successfully deleted.')
            career_detail.delete()
            return redirect('/career/detail/list/')