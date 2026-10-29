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

from django.views.generic import YearArchiveView, MonthArchiveView

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
# from news.models import *
# from news.forms import *

#Set Masking
# from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def news(request):
    assert isinstance(request, HttpRequest)
    menu = ['Beranda','Berita']
    title = 'Berita'

    news_query = News.objects.all().order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(news_query, per_page=5)

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'news':news,
        }

    return render(
        request,
        'frontend/news/news.html',
        context,
    )

def news_search(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Articles']
    title = 'Articles'

    query = request.GET.get("s")

    news_query = News.objects.filter(Q(name__icontains=query) | Q(publisher__icontains=query) | Q(information__icontains=query)).order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(news_query, per_page=10)

    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'news':news,
        }

    return render(
        request,
        'frontend/news/news.html',
        context,
    )

def news_detail(request, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Articles']
    title = 'Articles'

    decoded_id = decoding_id(id)
    all_news = News.objects.all().order_by('-id')
    news = News.objects.filter(id = decoded_id).first()

    context = {
        'title':title,
        'news':news,
        'all_news':all_news,
        }

    return render(
        request,
        'frontend/news/news_post.html',
        context
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def news_list(request):
    menu = ['Home','Daftar Berita']
    title = 'Berita'
    news = News.objects.all().order_by('-id')
    context = {
            'title':title,
            'menu':menu,
            'news':news
        }

    return render(
        request,
        'backend/news/news_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def news_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Tambah Berita'

    if request.method == 'POST':
        try:
            newsForm = NewsForm(data = request.POST, files = request.FILES)
            if newsForm.is_valid():
                news = newsForm.save()
                
                messages.add_message(request,messages.INFO,'Article '+news.name+' successfully added.')

                return redirect('/article/update/edit:'+str(encoding_id(news.id)))
            else:
                raise forms.ValidationError("Article is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Article was not added successfully.')
            newsForm = NewsForm(request.POST, request.FILES)

            context = {
                'title':title,
                'newsForm':newsForm,
            }
    
            return render(request,'backend/news/news_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Article was not added successfully.')
            newsForm = NewsForm(request.POST, request.FILES)

            context = {
                'title':title,
                'newsForm':newsForm,
            }
    
            return render(request,'backend/news/news_form.html',context)
    else:
        newsForm = NewsForm()

        context = {
            'title':title,
            'newsForm':newsForm,
            }

        return render(request,'backend/news/news_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def delete_attach(request, id):
    decoded_id = decoding_id(id)
    attach = News.objects.filter(id=decoded_id).first()
    attach.attachment = ''
    attach.save()

    messages.add_message(request,messages.WARNING,'Article attachment successfully deleted.')
    return redirect('/article/update/edit:'+str(encoding_id(attach.id)))

@login_required(login_url='/admin/who-login/')
@admin_only
def news_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Berita'

    id = decoding_id(id)
    
    news = News.objects.get_by_id(id = id)

    if request.method == 'POST':
        try:
            newsForm = NewsForm(data = request.POST, files = request.FILES, instance=news)

            if newsForm.is_valid():
                news = newsForm.save()
                
                messages.add_message(request,messages.INFO,'Article '+news.name+' successfully edited.')
                return redirect('/article/update/edit:'+str(encoding_id(news.id)))
            else:
                messages.add_message(request,messages.ERROR,'Article '+news.name+' failed to edit (else).')

                context = {
                'title':title,
                'newsForm':newsForm,
                'picture':'hidden',
                }
    
                return render(request,'backend/news/news_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Article '+news.name+' failed to edit (except).')
            newsForm = NewsForm(request.POST, request.FILES, instance=news)

            context = {
                'title':title,
                'newsForm':newsForm,
                'picture':'hidden',
            }
    
            return render(request,'backend/news/news_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            newsForm = NewsForm(instance=news)
            news = News.objects.filter(id=(id)).first()

            if news.attachment is not None:
                picture = 'show'
            else:
                picture = 'hidden'

            context = {
                'title':title,
                'newsForm':newsForm,
                'news':news,
                'picture':picture,
                }

            return render(request,'backend/news/news_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Article successfully deleted.')
            news.delete()
            return redirect('/article/list/')

# class ArticleYearArchiveView(YearArchiveView):
#     template_name = "frontend/news/news_archive.html"
#     queryset = News.objects.all()
#     date_field = "post_date"
#     make_object_list = True
#     allow_future = True

#     def get_context_data(self, **kwargs):
#         context = super(ArticleYearArchiveView, self).get_context_data(**kwargs)
#         news = News.objects.all()
#         context['title'] = 'Articles'
#         context['menu'] = ['Home','Articles']
#         context['news'] = news
#         return context

# class ArticleMonthArchiveView(MonthArchiveView):
#     template_name = "frontend/news/news_archive.html"
#     queryset = News.objects.all()
#     date_field = "post_date"
#     allow_future = True

#     def get_context_data(self, **kwargs):
#         context = super(ArticleMonthArchiveView, self).get_context_data(**kwargs)
#         news = News.objects.all()
#         context['title'] = 'Articles'
#         context['menu'] = ['Home','Articles']
#         context['news'] = news
#         return context
