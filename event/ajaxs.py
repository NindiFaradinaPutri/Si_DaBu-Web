from utils.utils import *
from app.decorators import *

import json

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q, BooleanField, CharField, Value, Sum, F, Case, When, Exists, Prefetch, Count
from django.db.models.functions import Coalesce, Concat
from django.db.models.fields.files import ImageFieldFile
from django.forms.models import model_to_dict
from django.forms import modelformset_factory

from django_tables2 import RequestConfig

from django.template import RequestContext
from django.template.loader import render_to_string

from datetime import datetime, date
from django.views.generic import ListView

from django.utils.safestring import mark_safe
from django.contrib.postgres.search import SearchVector
from decimal import Decimal
from django.db import IntegrityError, transaction

#EMAIL VERIFICATION AND TOKEN
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage

import hashlib
from uuid import uuid4
from rest_framework.authtoken.models import Token

from gallery.models import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def filter_gallery(request):
    if request.method == 'POST':
        gallery_query = Gallery.objects.all().order_by('-id')

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

        if not page or page == 'undefined':
            page = 1
        
        if not per_page or per_page == 'undefined':
            per_page = 9

        if not sort_by:
            sort_by = '-id'

        paginator = Paginator(gallery_query, per_page=per_page)

        try:
            gallery = paginator.page(page)
        except PageNotAnInteger:
            gallery = paginator.page(1)
        except EmptyPage:
            gallery = paginator.page(paginator.num_pages)

        context = {'gallery':gallery,}

        template = 'views/gallery.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def view_gallery(request):
    if request.method == 'POST':
        data_id = request.POST.get('data_id',None)

        data_id = decoding_id(data_id)

        gallery = Gallery.objects.filter(id = data_id).first()

        context = {
                'gallery':gallery,
                }
        template = 'views/gallery_view.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def create_event(request):
    if request.method == 'POST':
        data = request.POST.get('data',None)
        print(data)
        pass