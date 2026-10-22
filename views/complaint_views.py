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

#Set Loggin
import logging
logger = logging.getLogger(__file__)

#CUSTOM
from utils.utils import *
from app.decorators import *
from complaint.forms import *
from complaint.models import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def complaint_page(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Report']
    title = 'Report'    

    if request.method == 'POST':
        try:
            form = ComplaintForm(request.POST, request.FILES)

            if form.is_valid():
                data = form.save()
                complaint_response = ComplaintResponse.objects.create(complaint_id=data.id, status = ComplaintStatus.objects.filter(status = 'Open').first())
                
                messages.add_message(request,messages.SUCCESS,'Report successfully reported.')

                return redirect('/complaint/')
            else:
                messages.add_message(request,messages.ERROR,'Report was not added successfully.')
                form = ComplaintForm(request.POST, request.FILES)

                context = {
                'title':title,
                'form': form,
                }

                return render(
                    request,
                    'frontend/complaint/complaint.html',
                    context
                )
        except Exception as err:
            logger.info("Error Service: "+str(err))
            messages.add_message(request,messages.ERROR,'Report was not added successfully.')
            form = ComplaintForm(request.POST, request.FILES)

            context = {
            'title':title,
            'form': form,
            }

            return render(
                request,
                'frontend/complaint/complaint.html',
                context
            )
    else:
        form = ComplaintForm()

        context = {
        'title':title,
        'form': form,
        }

        return render(
            request,
            'frontend/complaint/complaint.html',
            context
        )
        
@login_required(login_url='/admin/who-login/')
@admin_only
def complaint_category_list(request):
    menu = ['Home','Laporan Kategori Keluhan']
    title = 'Laporan Kategori Keluhan'
    category = ComplaintCategory.objects.all().order_by('category')
    context = {
            'title':title,
            'menu':menu,
            'category':category
        }

    return render(
        request,
        'backend/complaint/complaint_category_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def complaint_category_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Tambah Kategori Keluhan'

    if request.method == 'POST':
        try:
            complaintCategoryForm = ComplaintCategoryForm(data = request.POST)
            if complaintCategoryForm.is_valid():
                complaintCategory = complaintCategoryForm.save()
                
                messages.add_message(request,messages.INFO,'New category successfully added.')

                return redirect('/complaint/category/edit:'+str(encoding_id(complaintCategory.id)))
            else:
                raise forms.ValidationError("FAQ is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Category was not added successfully.')
            complaintCategoryForm = ComplaintCategoryForm(request.POST)

            context = {
                'title':title,
                'complaintCategoryForm':complaintCategoryForm,
            }
    
            return render(request,'backend/complaint/complaint_category_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Category was not added successfully.')
            complaintCategoryForm = ComplaintCategoryForm(request.POST)

            context = {
                'title':title,
                'complaintCategoryForm':complaintCategoryForm,
            }
    
            return render(request,'backend/complaint/complaint_category_form.html',context)
    else:
        complaintCategoryForm = ComplaintCategoryForm()

        context = {
            'title':title,
            'complaintCategoryForm':complaintCategoryForm,
            }

        return render(request,'backend/complaint/complaint_category_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def complaint_category_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Laporan Kategori Keluhan'

    id = decoding_id(id)
    
    complaintCategory = ComplaintCategory.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            complaintCategoryForm = ComplaintCategoryForm(data = request.POST, instance=complaintCategory)

            if complaintCategoryForm.is_valid():
                complaintCategory = complaintCategoryForm.save()
                
                messages.add_message(request,messages.INFO,'Category successfully edited.')
                return redirect('/complaint/category/edit:'+str(encoding_id(complaintCategory.id)))
            else:
                messages.add_message(request,messages.ERROR,+'Failed to edit category (else).')

                context = {
                'title':title,
                'complaintCategoryForm':complaintCategoryForm,
                }
    
                return render(request,'backend/complaint/complaint_category_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Failed to edit category (except).')
            complaintCategoryForm = ComplaintCategoryForm(request.POST, instance=complaintCategory)

            context = {
                'title':title,
                'complaintCategoryForm':complaintCategoryForm,
            }
    
            return render(request,'backend/complaint/complaint_category_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            complaintCategoryForm = ComplaintCategoryForm(instance=complaintCategory)

            context = {
                'title':title,
                'complaintCategoryForm':complaintCategoryForm,
                }

            return render(request,'backend/complaint/complaint_category_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Category successfully deleted.')
            complaintCategory.delete()
            return redirect('/complaint/category/')

@login_required(login_url='/admin/who-login/')
@admin_only
def complaint_list(request):
    menu = ['Home','Laporan Keluhan']
    title = 'Laporan Keluhan'
    complaint = Complaint.objects.all().order_by('-creation_date')
    context = {
            'title':title,
            'menu':menu,
            'complaint':complaint
        }

    return render(
        request,
        'backend/complaint/complaint_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def complaint_view(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Report Detail'

    id = decoding_id(id)

    message = Complaint.objects.filter(id = id).first()
    check = message.attachment

    if check:
        check = str(check)
        check = check.split(".")
        for i in check:
	        check = i
        if check == 'jpg' or check == 'jpeg' or check == 'png' or check == 'PNG' or check == 'JPG' or check == 'JPEG':
            is_image = True
        else: 
            is_image = False
    else:
        is_image = None

    if message:
        if status == 'view':
            response_list = ComplaintResponse.objects.filter(complaint_id = id)
            if response_list:
                response = response_list.latest('id')
            else:
                response = None

            if response:
                responseForm = ComplaintResponseForm()
                responseForm.fields['user'].initial = request.user
                responseForm.fields['status'].initial = getattr(response.status, 'id', None)
            else:
                responseForm = ComplaintResponseForm()
                responseForm.fields['user'].initial = request.user
            context = {
                'title':title, 
                'complaint_id':id,
                'is_image': is_image,
                'message':message,
                'response_list':response_list,
                'responseForm':responseForm,}
            return render(request,'backend/complaint/complaint_view.html',context)