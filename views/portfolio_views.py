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
from portfolio.models import *
from portfolio.forms import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def services(request):
    assert isinstance(request, HttpRequest)
    menu = ['Beranda','Kegiatan']
    title = 'Kegiatan'

    services_query = Service.objects.all().order_by('id')

    client = Client.objects.all()

    page = request.GET.get('page',1)

    paginator = Paginator(services_query, per_page=10)

    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'services':services,
        'client':client,
        }

    return render(
        request,
        'frontend/services/services.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def services_list(request):
    menu = ['Home','Services List']
    title = 'Services'
    services = Service.objects.all().order_by('name')
    context = {
            'title':title,
            'menu':menu,
            'services':services
        }

    return render(
        request,
        'backend/services/services_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def services_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add New Service'
    menu = ['Service', 'Add New Service']

    serviceFormSet = modelformset_factory(ServicePhoto, form=ServicePhotoForm, extra=1)
    
    if request.method == 'POST':
        try:
            serviceForm = ServiceForm(request.POST)
            servicePhotoSet = serviceFormSet(request.POST, request.FILES, queryset=ServicePhoto.objects.none(), prefix='form')

            if serviceForm.is_valid() and servicePhotoSet.is_valid():
                service = serviceForm.save()
                
                for form in servicePhotoSet:
                    if form.is_valid() and service:
                        photo = form.save(commit=False)
                        photo.service = service
                        photo.save()
                messages.add_message(request,messages.SUCCESS,'Service ' + service.name + ' successfully added.')

                return redirect('/services/update/edit:'+str(encoding_id(service.id)))
            else:
                messages.add_message(request,messages.ERROR,'Service was not added successfully.')
                serviceForm = ServiceForm(request.POST)
                servicePhotoSet = serviceFormSet(request.POST, request.FILES, queryset=ServicePhoto.objects.none(), prefix='form')

                context = {'title':title,
                            'menu':menu,
                            'serviceForm':serviceForm,
                            'servicePhotoSet':servicePhotoSet,
                            }
                return render(request, 'backend/services/services_form.html',context)
        except Exception as err:
            logger.info("Error Service: "+str(err))
            messages.add_message(request,messages.ERROR,'Service was not added successfully.')
            serviceForm = ServiceForm(request.POST)
            servicePhotoSet = serviceFormSet(request.POST, request.FILES, queryset=ServicePhoto.objects.none(), prefix='form')

            context = {'title':title,
                        'menu':menu,
                        'serviceForm':serviceForm,
                        'servicePhotoSet':servicePhotoSet,
                        }
            return render(request, 'backend/services/services_form.html',context)
    else:
        serviceForm = ServiceForm()
        servicePhotoSet = serviceFormSet(queryset=ServicePhoto.objects.none(), prefix='form')

        context = {'title':title,
                    'menu':menu,
                    'serviceForm':serviceForm,
                    'servicePhotoSet':servicePhotoSet,
                    }
        return render(request, 'backend/services/services_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def services_update(request, status, id):
    id = decoding_id(id)
    if not id:
        return redirect('/')

    assert isinstance(request, HttpRequest)
    title = 'Update Service'
    menu = ['Service', 'Update Service']

    selected_service = Service.objects.get(id = id)
    serviceFormSet = modelformset_factory(ServicePhoto, form=ServicePhotoEditForm, extra=0)

    if request.method == 'POST':
        try:
            serviceForm = ServiceForm(request.POST, instance=selected_service)
            servicePhotoSet = serviceFormSet(request.POST, request.FILES, queryset=ServicePhoto.objects.filter(service_id = id), prefix='form')
            if serviceForm.is_valid():
                service = serviceForm.save()

            if servicePhotoSet.is_valid():
                for form in servicePhotoSet:
                    if form.cleaned_data.get('delete_item') == True:
                        data = form.save(commit=False)
                        data.delete()
                    elif form.is_valid() and service:
                        photo = form.save(commit=False)
                        photo.service = service
                        photo.save()
            
            return redirect('/services/update/edit:'+str(encoding_id(service.id)))
        except Exception as err:
            logger.info("Error Service: "+str(err))
            messages.add_message(request,messages.ERROR,'Failed to update the service.')
            serviceForm = ServiceForm(request.POST, instance=selected_service)
            servicePhotoSet = serviceFormSet(request.POST, request.FILES, queryset=ServicePhoto.objects.filter(service_id = id), prefix='form')

            context = {'title':title,
                        'menu':menu,
                        'serviceForm':serviceForm,
                        'servicePhotoSet':servicePhotoSet,
                        }
            return render(request, 'backend/services/services_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            serviceForm = ServiceForm(instance=selected_service)
            servicePhotoSet = serviceFormSet(queryset=ServicePhoto.objects.filter(service_id = id), prefix='form')

            context = {'title':title,
                        'menu':menu,
                        'serviceForm':serviceForm,
                        'servicePhotoSet':servicePhotoSet,
                        }
            return render(request, 'backend/services/services_form.html',context)
        elif status == 'delete' and selected_service:
            messages.add_message(request,messages.INFO,'Service '+selected_service.service_name+' successfully deleted.')
            selected_service.delete()
            return redirect('/services/list/')

@login_required(login_url='/admin/who-login/')
@admin_only
def portfolio_list(request):
    assert isinstance(request, HttpRequest)
    title = 'Portfolio'
    menu = ['Jasa', 'Seleksi Jasa']

    portfolio = Portfolio.objects.all().order_by('-id')
    #portfolio_photo = PortfolioAttachment.objects.all()

    context = {
                'title':title,
                'portfolio':portfolio,
                }
    return render(request, 'backend/portfolios/portfolio_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def portfolio_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add Portfolio'

    service = Service.objects.all().order_by('name')

    PortfolioFormSet = modelformset_factory(PortfolioAttachment, form=PortfolioAttachmentForm, extra=1)

    if request.method == 'POST':
        try:
            portfolioform = PortfolioForm(request.POST)
            portfoliophotoform = PortfolioFormSet(request.POST, request.FILES, queryset=PortfolioAttachment.objects.none(), prefix='form')

            if portfolioform.is_valid() and portfoliophotoform.is_valid():
                portfolio =  portfolioform.save()
                
                tags = request.POST.getlist('tags')
                for tag in tags:
                    p = PortfolioTags.objects.create(portfolio = portfolio, tags = tag)

                for form in portfoliophotoform:
                    if form.is_valid() and portfolio:
                        attachment = form.save(commit=False)
                        attachment.portfolio = portfolio
                        attachment.save()
                        
                    else:
                        messages.add_message(request,messages.INFO,'Picture is not valid.')

                        portfolioform = PortfolioForm(data = request.POST)
                        portfoliophotoform = PortfolioAttachmentForm(data = request.POST, files = request.FILES)

                        context = {
                        'title':title,
                        'portfolioform':portfolioform,
                        'portfoliophotoform':portfoliophotoform,
                        'tags':tags
                        }

                        return render(request,'backend/portfolios/portfolio_form.html',context)

                messages.add_message(request,messages.INFO,'Portfolio was added successfully.')

                return redirect('/portfolios/list/')
            else:
                raise forms.ValidationError("Failed to save the data.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'{Portfolio tidak berhasil ditambahkan.')
            portfolioform = PortfolioForm(data = request.POST)
            portfoliophotoform = PortfolioAttachmentForm(data = request.POST, files = request.FILES)

            context = {
            'title':title,
            'portfolioform':portfolioform,
            'tags':tags
            }

            return render(request,'backend/portfolios/portfolio_form.html',context)

        except Exception as e:
            messages.add_message(request,messages.ERROR,'Portfolio was not added successfully.')
            portfolioform = PortfolioForm(data = request.POST)
            portfoliophotoform = PortfolioAttachmentForm(data = request.POST, files = request.FILES)

            context = {
            'title':title,
            'portfolioform':portfolioform,
            'portfoliophotoform':portfoliophotoform,
            'tags':tags
            }

            return render(request,'backend/portfolios/portfolio_form.html',context)
    else:
        portfolioform = PortfolioForm()

        portfoliophotoSet = PortfolioFormSet(queryset=PortfolioAttachment.objects.none(), prefix='form')

        context = {
            'title':title,
            'portfolioform':portfolioform,
            'portfoliophotoSet':portfoliophotoSet,
            }

        return render(request,'backend/portfolios/portfolio_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def portfolio_update(request, status, id):
    id = decoding_id(id)
    if not id:
        return redirect('/')

    assert isinstance(request, HttpRequest)
    title = 'Update Portfolio'
  
    portfolio = Portfolio.objects.get(id = id)
    tags = PortfolioTags.objects.filter(portfolio = portfolio)

    PortfolioFormSet = modelformset_factory(PortfolioAttachment, form=PortfolioAttachmentEditForm, extra=0)

    if request.method == 'POST':
        portfolioform = PortfolioForm(request.POST, instance=portfolio)
        portfoliophotoform = PortfolioFormSet(request.POST, request.FILES, queryset=PortfolioAttachment.objects.filter(portfolio_id = id), prefix='form')

        if portfolioform.is_valid() and portfoliophotoform.is_valid():
            portfolio =  portfolioform.save()

            tags = request.POST.getlist('tags')
            clear_tags = PortfolioTags.objects.filter(portfolio = portfolio).order_by('-id')
            clear_tags.delete()
            for tag in tags:
                p = PortfolioTags.objects.create(portfolio = portfolio, tags = tag)
                
            for form in portfoliophotoform:
                if form.cleaned_data.get('delete_item') == True:
                    data = form.save(commit=False)
                    data.delete()
                elif form.is_valid() and portfolio:
                    attachment = form.save(commit=False)
                    attachment.portfolio = portfolio
                    attachment.save()
                else:
                    messages.add_message(request,messages.INFO,'Picture is not valid.')

                    portfolioform = PortfolioForm(data = request.POST)
                    portfoliophotoform = PortfolioAttachmentForm(data = request.POST, files = request.FILES)

                    context = {
                    'title':title,
                    'portfolioform':portfolioform,
                    'portfoliophotoform':portfoliophotoform,
                    'tags':tags,
                    }

                    return render(request,'backend-user/portfolio_form.html',context)

            messages.add_message(request,messages.INFO,'Portfolio was added successfully.')

            return redirect('/portfolios/list/')
        else:
            raise forms.ValidationError("Failed to save the data.")

    elif request.method == 'GET':
        if status == 'edit':
            portfolioform = PortfolioForm(instance=portfolio)
            portfolioform.fields['service'].selected = portfolio.service

            portfoliophotoset = PortfolioFormSet(queryset=PortfolioAttachment.objects.filter(portfolio_id = id), prefix='form')
            
            if portfolio.is_active == True:
                portfolioform.fields['is_active'].initial = 1
            else:
                portfolioform.fields['is_active'].initial = 0

            context = {
                'title':title,
                'portfolioform':portfolioform,
                'portfoliophotoSet':portfoliophotoset,
                'tags':tags,
                }

            return render(request,'backend/portfolios/portfolio_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Portfolio '+portfolio.title+' successfully deleted.')
            portfolio.delete()
            return redirect('/portfolios/list/')

def portfolio(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Portfolio']
    title = 'Portfolio'

    portfolio_query = Portfolio.objects.filter(is_active = True).order_by('-id')

    services = Service.objects.all().order_by('id')
    tags = PortfolioTags.objects.all().distinct('tags')

    testimony = Testimony.objects.all().order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(portfolio_query, per_page=9)

    try:
        portfolio = paginator.page(page)
    except PageNotAnInteger:
        portfolio = paginator.page(1)
    except EmptyPage:
        portfolio = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'portfolio':portfolio,
        'testimony':testimony,
        'services':services,
        'tags':tags,
        'ajax':'false'
        }

    return render(
        request,
        'frontend/portfolio/portfolio.html',
        context,
    )

def portfolio_service(request, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Portfolio']
    title = 'Portfolio'

    id = decoding_id(id)

    portfolio_query = Portfolio.objects.filter(is_active = True, service = id).order_by('-id')

    services = Service.objects.all().order_by('id')
    tags = PortfolioTags.objects.all().distinct('tags')

    testimony = Testimony.objects.all()

    page = request.GET.get('page',1)

    paginator = Paginator(portfolio_query, per_page=9)

    try:
        portfolio = paginator.page(page)
    except PageNotAnInteger:
        portfolio = paginator.page(1)
    except EmptyPage:
        portfolio = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'portfolio':portfolio,
        'testimony':testimony,
        'services':services,
        'tags':tags,
        'ajax':'false'
        }

    return render(
        request,
        'frontend/portfolio/portfolio.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def testimony_list(request):
    assert isinstance(request, HttpRequest)
    title = 'Testimony'
    menu = ['Jasa', 'Seleksi Jasa']

    testimony = Testimony.objects.all().order_by('-id')

    context = {
                'title':title,
                'testimony':testimony,
                }
    return render(request, 'backend/testimony/testimony_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def testimony_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Testimony Form'

    if request.method == 'POST':
        #try:
            form = TetstimonyForm(request.POST, request.FILES)
            if form.is_valid():
                testimonyform = form.save()
                messages.add_message(request,messages.INFO,'Testimony was successfully added.')

                return redirect('/testimony/list/')
            else:
                raise forms.ValidationError("Data is invalid.")
        #except ValidationError as e:
        #    messages.add_message(request,messages.ERROR,'Testimony was not added successfully.')
        #    form = TetstimonyForm(request.POST, request.FILES)

        #    context = {
        #        'title':title,
        #        'form':form,
        #    }
    
        #    return render(request,'backend/testimony/testimony_form.html',context)
        #except Exception as e:
        #    messages.add_message(request,messages.ERROR,'Testimony was not added successfully.')
        #    form = TetstimonyForm(request.POST, request.FILES)

        #    context = {
        #        'title':title,
        #        'form':form,
        #    }
    
        #    return render(request,'backend/testimony/testimony_form.html',context)
    else:
        form = TetstimonyForm()

        context = {
            'title':title,
            'form':form,
            }

        return render(request,'backend/testimony/testimony_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def testimony_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Testimony'

    id = decoding_id(id)
    
    testimony = Testimony.objects.filter(id = id).first()

    if request.method == 'POST':
        try:
            testimonyForm = TetstimonyForm(request.POST, request.FILES, instance=testimony)

            if testimonyForm.is_valid():
                testimonyForm = testimonyForm.save()
                
                messages.add_message(request,messages.INFO,''+testimony.name+' successfully edited.')
                return redirect('/testimony/list/')
            else:
                messages.add_message(request,messages.ERROR,''+testimony.name+' failed to edit.')

                context = {
                'title':title,
                'form':testimonyForm,
                'picture':'hidden',
                }
    
                return render(request,'backend/testimony/testimony_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,''+testimony.name+' failed to edit (except).')
            testimonyForm = TetstimonyForm(request.POST, request.FILES, instance=testimony)

            context = {
                'title':title,
                'form':testimonyForm,
                'picture':'hidden',
            }
    
            return render(request,'backend/testimony/testimony_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            testimonyForm = TetstimonyForm(instance=testimony)

            context = {
                'title':title,
                'form':testimonyForm,
                }

            return render(request,'backend/testimony/testimony_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,''+testimony.name+' successfully deleted.')
            testimony.delete()
            return redirect('/testimony/list/')

@login_required(login_url='/admin/who-login/')
@admin_only
def client_list(request):
    assert isinstance(request, HttpRequest)
    title = 'Partner'
    menu = ['Jasa', 'Seleksi Jasa']

    client = Client.objects.all().order_by('-id')

    context = {
                'title':title,
                'client':client,
                }
    return render(request, 'backend/client/client_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def client_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Partner Form'

    if request.method == 'POST':
        #try:
            
            form = ClientForm(request.POST, request.FILES)
            for field in form:
                print("Field Error:", field.name,  field.errors)
            if form.is_valid():
                testimonyform = form.save()
                messages.add_message(request,messages.INFO,'Client data was successfully added.')

                return redirect('/client/list/')
            else:
                for field in form:
                    raise forms.ValidationError("Data is invalid."+ field.name + field.errors)
        #except ValidationError as e:
        #    messages.add_message(request,messages.ERROR,'Testimony was not added successfully.')
        #    form = TetstimonyForm(request.POST, request.FILES)

        #    context = {
        #        'title':title,
        #        'form':form,
        #    }
    
        #    return render(request,'backend/testimony/testimony_form.html',context)
        #except Exception as e:
        #    messages.add_message(request,messages.ERROR,'Testimony was not added successfully.')
        #    form = TetstimonyForm(request.POST, request.FILES)

        #    context = {
        #        'title':title,
        #        'form':form,
        #    }
    
        #    return render(request,'backend/testimony/testimony_form.html',context)
    else:
        form = ClientForm()

        context = {
            'title':title,
            'form':form,
            }

        return render(request,'backend/client/client_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def client_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Partner'

    id = decoding_id(id)
    
    client = Client.objects.filter(id = id).first()

    if request.method == 'POST':
        try:
            form = ClientForm(request.POST, request.FILES, instance=client)

            if form.is_valid():
                clientform = form.save()
                
                messages.add_message(request,messages.INFO,''+clientform.name+' successfully edited.')
                return redirect('/client/list/')
            else:
                messages.add_message(request,messages.ERROR,'Failed to edit.')

                context = {
                'title':title,
                'form':form,
                }
    
                return render(request,'backend/client/client_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,''+team.name+' failed to edit (except).')
            form = ClientForm(request.POST, request.FILES, instance=client)

            context = {
                'title':title,
                'form':form,
                'picture':'hidden',
            }
    
            return render(request,'backend/client/client_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            form = ClientForm(instance=client)

            context = {
                'title':title,
                'form':form,
                }

            return render(request,'backend/client/client_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,''+client.name+' successfully deleted.')
            client.delete()
            return redirect('/client/list/')

