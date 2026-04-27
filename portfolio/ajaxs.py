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

from portfolio.models import *
from portfolio.filters import *
from portfolio.forms import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def addform_servicephoto(request):
    if request.method == 'POST':
        form_count = request.POST.get('form_count',1)

        servicePhotoForm = ServicePhotoForm()
        form_title = 'Service Photo'
        id_form = 'id_formappend_'+str(int(form_count)-1)
        id_prefix = 'id_form-'+str(int(form_count)-1)
        prefix = 'form-'+str(int(form_count)-1)

        context = {
                'id_prefix':id_prefix,
                'prefix':prefix,
                'form_title':form_title,
                'counter':form_count,
                'id_form':id_form,
                'form':servicePhotoForm,
                }
        template = 'template/forms/tmp_formappend.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def filter_service(request):
    if request.method == 'POST':
        services_query = Service.objects.all().order_by('name')

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

        if not page or page == 'undefined':
            page = 1
        
        if not per_page or per_page == 'undefined':
            per_page = 10

        if not sort_by:
            sort_by = '-id'

        paginator = Paginator(news_query, per_page=per_page)

        try:
            services = paginator.page(page)
        except PageNotAnInteger:
            services = paginator.page(1)
        except EmptyPage:
            services = paginator.page(paginator.num_pages)

        context = {'services':services,}

        template = 'views/services.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def addform_portfoliophoto(request):
    if request.method == 'POST':
        form_count = request.POST.get('form_count',1)

        servicePhotoForm = PortfolioAttachmentForm()
        form_title = 'Portfolio Photo'
        id_form = 'id_formappend_'+str(int(form_count)-1)
        id_prefix = 'id_form-'+str(int(form_count)-1)
        prefix = 'form-'+str(int(form_count)-1)

        context = {
                'id_prefix':id_prefix,
                'prefix':prefix,
                'form_title':form_title,
                'counter':form_count,
                'id_form':id_form,
                'form':servicePhotoForm,
                }
        template = 'template/forms/tmp_formappend.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def view_portfolio(request):
    if request.method == 'POST':
        data_id = request.POST.get('data_id',None)

        data_id = decoding_id(data_id)

        portfolio = Portfolio.objects.get(id = data_id)
        portfoliophoto = PortfolioAttachment.objects.filter(portfolio = portfolio)

        tags = PortfolioTags.objects.filter(portfolio = portfolio)

        context = {
                'portfolio':portfolio,
                'portfoliophoto':portfoliophoto,
                'tags':tags
                }
        template = 'views/portfolio_view.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def ctrg_portfolio(request):
    if request.method == 'POST':
        data_id = request.POST.get('data_id',None)
        type = request.POST.get('type',None)

        if type == 'tags':
            tags = PortfolioTags.objects.filter(tags = data_id)
            portfoliophoto = PortfolioAttachment.objects.all()

            context = {
                    'portfolio_photo':portfoliophoto,
                    'tags':tags,
                    'ajax':'true'
                    }
            template = 'views/portfolio_list.html'
            html = render_to_string(template_name=template, context=context, request = request, using=None)
            return HttpResponse(html)
        else:
            data_id = decoding_id(data_id)

            portfolio = Portfolio.objects.filter(service__id = data_id)
            portfoliophoto = PortfolioAttachment.objects.all()

            context = {
                    'portfolio':portfolio,
                    'portfolio_photo':portfoliophoto,
                    'ajax':'false'
                    }
            template = 'views/portfolio_list.html'
            html = render_to_string(template_name=template, context=context, request = request, using=None)
            return HttpResponse(html)

def filter_portfolio(request):
    if request.method == 'POST':
        query_portfolio = Portfolio.objects.all().order_by('-id')

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

        if not page or page == 'undefined':
            page = 1
        
        if not per_page or per_page == 'undefined':
            per_page = 9

        if not sort_by:
            sort_by = '-id'

        paginator = Paginator(query_portfolio, per_page=per_page)

        try:
            portfolio = paginator.page(page)
        except PageNotAnInteger:
            portfolio = paginator.page(1)
        except EmptyPage:
            portfolio = paginator.page(paginator.num_pages)

        context = {'portfolio':portfolio,'ajax':'false'}

        template = 'views/portfolio_list.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def view_service(request):
    if request.method == 'POST':
        data_id = request.POST.get('data_id',None)

        data_id = decoding_id(data_id)

        service = Service.objects.get(id = data_id)

        context = {
                'service':service,
                }
        template = 'views/service.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)