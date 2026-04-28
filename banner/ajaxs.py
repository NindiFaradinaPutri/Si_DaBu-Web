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

from authentication.models import *
from authentication.auth_forms import *

from banner.models import *
from banner.filters import *
from banner.ads_forms import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def filter_video(request):
    if request.method == 'POST':
        queryset = PhotoVideoAdsPost.objects.filter(video__isnull = False).order_by('-id')
        video_filter = PhotoVideoAdsFilter(request.POST, queryset=queryset)

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

        if not sort_by:
            sort_by = '-id'

        if not per_page:
            per_page = 20

        queryset = video_filter.qs.order_by(sort_by)

        paginator = Paginator(queryset,per_page=per_page)

        try:
            list_video = paginator.page(page)
        except PageNotAnInteger:
            list_video = paginator.page(1)
        except EmptyPage:
            list_video = paginator.page(paginator.num_pages)

        context = {'list_video':list_video,}

        template = 'template/views/view_video_list.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def current_video(request):
    if request.method == 'POST':
        user = request.user
        id_video = request.POST.get('id_video')

        selected_video = PhotoVideoAdsPost.objects.filter(id = id_video).first()

        html = mark_safe(''' 
                        <video width="350" height="auto" controls autoplay>
                            <source src="%s" type="audio/mp4" id="current_video" />
                        </video>
                        '''% (selected_video.video.url))
        
        return HttpResponse(html)

def filter_photo(request):
    if request.method == 'POST':
        queryset = PhotoVideoAdsPost.objects.filter(photo__isnull = False).order_by('-id')
        photo_filter = PhotoVideoAdsFilter(request.POST, queryset=queryset)

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

        if not sort_by:
            sort_by = '-id'

        if not per_page:
            per_page = 20

        queryset = photo_filter.qs.order_by(sort_by)

        paginator = Paginator(queryset,per_page=per_page)

        try:
            list_photo = paginator.page(page)
        except PageNotAnInteger:
            list_photo = paginator.page(1)
        except EmptyPage:
            list_photo = paginator.page(paginator.num_pages)

        context = {'list_photo':list_photo,}

        template = 'template/views/view_photo_list.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def current_photo(request):
    if request.method == 'POST':
        id_photo = request.POST.get('id_photo')

        selected_photo = PhotoVideoAdsPost.objects.filter(id = id_photo).first()

        html = mark_safe(''' <img src="%s" alt="" id="current_photo" style="max-width:500px; height:auto;">
                        '''% (selected_photo.photo.url))
        
        return HttpResponse(html)