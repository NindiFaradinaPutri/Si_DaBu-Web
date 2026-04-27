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

    profile = Profile.objects.filter(id = 1).first()

    banner = Banner.objects.filter(category = 2).order_by('id')

    context = {
            'title':'Halaman Beranda',
            'kegiatans':kegiatans,
            'client':client,
            'profile':profile,
            'banner':banner,
        }
      

    return render(
        request,
        'frontend/home/index.html',
        context,
    )

def event_frontend(request):
    menu = ['Beranda','Sejarah Kami']

    profile = Profile.objects.filter(id = 1).first()
    contact = Contact.objects.filter(id = 1).first()
    client = Client.objects.all()
    tech = Technology.objects.all()
    naration = TeamNaration.objects.filter(id = 1).first()

    context = {
            'title':'Sejarah Kami',
            'menu':menu,
            'profile':profile,
            'contact':contact,
            'client':client,
            'tech':tech,
            'naration':naration,
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

