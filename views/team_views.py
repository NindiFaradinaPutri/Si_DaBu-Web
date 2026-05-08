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

from app.decorators import *
from team.models import *
from team.forms import *
from utils.utils import *

#Set Logg
import logging
logger = logging.getLogger(__file__)

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

@login_required(login_url='/admin/who-login/')
@admin_only
def team_list(request):
    assert isinstance(request, HttpRequest)
    title = 'Pengurus'

    team = Team.objects.all().order_by('order','id')

    context = {
                'title':title,
                'team':team,
                }
    return render(request, 'backend/team/team_list.html',context)

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

@login_required(login_url='/admin/who-login/')
@admin_only
def naration_update(request):
    assert isinstance(request, HttpRequest)

    menu = ['Home','Perbarui Narasi Walpaper']

    naration = TeamNaration.objects.filter(id = 1).first()

    if request.method == 'POST':
        try:
            if naration:
                form = NarationForm(request.POST, instance = naration)
            else:
                form = NarationForm(request.POST)
            
            if form.is_valid():
                form.save()

                messages.add_message(request,messages.INFO,'Success updating naration.')
                return redirect('/naration/')
            else:
                messages.add_message(request,messages.ERROR,'Failed to do update the naration.')
                context = {
                'title':'Perbarui Narasi Walpaper',
                'menu':menu,
                'form':form,
                'naration':naration
                }

            return render(request,'backend/team/naration_form.html',context)

        except Exception as err:
            logger.info("Error Update Naration: "+str(err))
            messages.add_message(request,messages.ERROR,'Failed to do update.')

            form = NarationForm(request.POST)

            context = {
                'title':'Perbarui Narasi Walpaper',
                'menu':menu,
                'form':form,
                'naration':naration
            }

            return render(request,'backend/team/naration_form.html',context)
    else:
        if naration:
            form = NarationForm(instance = naration)
        else:
            form = NarationForm()

        context = {
                'title':'Perbarui Narasi Walpaper',
                'menu':menu,
                'form':form,
                'naration':naration
            }

        return render(request,'backend/team/naration_form.html',context)


@login_required(login_url='/admin/who-login/')
@admin_only
def iqamah_update(request):

    iqamah = BannerIqamah.objects.filter(id=1).first()

    if request.method == 'POST':
        try:
            form = IqamahForm(
                request.POST,
                request.FILES,   # 🔥 WAJIB untuk photo upload
                instance=iqamah
            )

            if form.is_valid():
                form.save()

                messages.success(request, "Iqamah berhasil diperbarui")
                return redirect('/iqamah/')
            else:
                messages.error(request, "Validasi gagal")

        except Exception as err:
            logger.info(f"Error Update Iqamah: {err}")
            messages.error(request, "Terjadi kesalahan saat update")

            form = IqamahForm(request.POST, request.FILES, instance=iqamah)

        return render(request, 'backend/team/iqamah_form.html', {
            'form': form,
            'iqamah': iqamah,
            'title': 'Perbarui Iqamah'
        })

    else:
        form = IqamahForm(instance=iqamah)

    return render(request, 'backend/team/iqamah_form.html', {
        'form': form,
        'iqamah': iqamah,
        'title': 'Perbarui Iqamah'
    })