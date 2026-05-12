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
from django.utils.encoding import force_bytes, force_text

#Test Exception
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

from app.decorators import *
from utils.utils import *
from profile.models import *
from profile.forms import *
from complaint.forms import *
from complaint.models import *


#Set Logg
import logging
logger = logging.getLogger(__file__)

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#About
@login_required(login_url='/admin/who-login/')
@admin_only
def profile(request):
    assert isinstance(request, HttpRequest)

    menu = ['Silatama','Profile']

    profile = Profile.objects.filter(id = 1).first()

    if request.method == 'POST':
        try:
            if profile:
                form = ProfileForm(request.POST, instance = profile)
            else:
                form = ProfileForm(request.POST)
            
            if form.is_valid():
                form.save()

                messages.add_message(request,messages.INFO,'Update Success.')
                return redirect('/profile/')
            else:
                context = {
                'title':'Form',
                'menu':menu,
                'form':form,
                'profile':profile
                }

            return render(request,'backend/about/about_view.html',context,)

        except Exception as err:
            logger.info("Error Service: "+str(err))
            messages.add_message(request,messages.ERROR,'Failed to do update.')

            form = ProfileForm(request.POST)

            context = {
                'title':'Form',
                'menu':menu,
                'form':form,
                'profile':profile
            }

            return render(request,'backend/about/about_view.html',context,)
    else:
        if profile:
            form = ProfileForm(instance = profile)
        else:
            form = ProfileForm()

        context = {
                'title':'Form',
                'menu':menu,
                'form':form,
                'profile':profile
            }

        return render(request,'backend/about/about_view.html',context,)

#CONTACT

def contact_us(request):
    assert isinstance(request, HttpRequest)

    menu = ['Home', 'Report']
    title = 'Report'
    contact = Contact.objects.filter(id=1).first()

    if request.method == 'POST':
        
        form = ComplaintForm(request.POST, request.FILES)

        try:
            if form.is_valid():
                data = form.save()

                Complaint_name,created =ComplaintResponse.objects.get_or_create(
                    complaint_id=data.id,
                    status=ComplaintStatus.objects.filter(status='Open').first()
                )
                
                
                Complaint_subject=Complaint.objects.filter(id=Complaint_name.complaint_id).first()
                
                name_complaint = Complaint_subject.subject
                # ambil domain
                current_site = get_current_site(request)

                mail_subject = f'category complaint {data.category}'

                message = render_to_string(
                    'template/registrations/account_activation.html',
                    {
                        'profile': data,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(data.id)),
                        'token': 'dummy-token',
                        'nama':data.sender,
                        'email': data.email,
                        'subject': data.subject,
                        'category': data.category,
                        'phone': data.telphone,
                        'message_user': data.information,
                        'date': data.creation_date,
                        'image': request.build_absolute_uri(data.attachment.url) if data.attachment else None,
                        
                    }
                )

                email = EmailMessage(
                    mail_subject,
                    message,
                    to=['abidhype@gmail.com']
                )

                email.content_subtype = "html"

                # kirim email (debug aktif)
                email.send(fail_silently=False)

                messages.success(request, 'Report successfully reported.')
                return redirect('/contact/')

            else:
                messages.error(request, 'Report was not added successfully.')

        except Exception as e:
            print("EMAIL ERROR:", e)
            logger.info("Error Service: " + str(e))
            messages.error(request, 'Report was not added successfully.')

    else:
        form = ComplaintForm()

    return render(
        request,
        'frontend/contact/contact.html',
        {
            'title': title,
            'form': form,
            'contact': contact,
        }
    )

def contact_submit(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Contact Us']
    title = 'Contact Us'
    faq = FAQ.objects.all().order_by('id')

    if request.method == "POST":
        recaptchaform = ReCaptcha(request.POST)
        if recaptchaform.is_valid():
            name = request.POST.get('name', None)
            email = request.POST.get('email', None)
            subject = request.POST.get('subject', None)
            message = request.POST.get('message', None)

            current_site = get_current_site(request)
            mail_subject = subject
            contact_message = render_to_string('views/view_contact_message.html', {
                'name': name,
                'email': email,
                'message': message,
                'subject': subject,
            })
            email_profile = Contact.objects.filter(id=1).first()

            if email_profile:
                to_email = str(email_profile.email)
            else:
                to_email = 'info@silatama.co.id'
            email = EmailMessage(
                mail_subject, contact_message, to=[to_email]
            )
            email.send()

            recaptchaform = ReCaptcha()

            context = {
                'title':title,
                'recaptchaform':recaptchaform,
                'data':'success',
                'faq':faq,
                }

            return render(
                request,
                'frontend/contact/contact.html',
                context
            )
        else:
            logger.info("Error Captcha")
            messages.add_message(request,messages.ERROR,'Please check the captcha')
            recaptchaform = ReCaptcha()

            context = {
                'title':title,
                'recaptchaform':recaptchaform,
                'data':'error',
                'faq':faq,
                }

            return render(
                request,
                'frontend/contact/contact.html',
                context
            )
    else:
        recaptchaform = ReCaptcha()
        faq = FAQ.objects.all().order_by('id')

        context = {
            'title':title,
            'recaptchaform':recaptchaform,
            'faq':faq,
            }

        return render(
            request,
            'frontend/contact/contact.html',
            context
        )

@login_required(login_url='/admin/who-login/')
@admin_only
def contact_update(request):
    assert isinstance(request, HttpRequest)

    menu = ['Home','Perbarui Kontak']

    contact = Contact.objects.filter(id = 1).first()

    if request.method == 'POST':
        try:
            if contact:
                form = ContactForm(request.POST, instance = contact)
            else:
                form = ContactForm(request.POST)
            
            if form.is_valid():
                form.save()

                messages.add_message(request,messages.INFO,'Success updating contact.')
                return redirect('/contact/update/')
            else:
                messages.add_message(request,messages.ERROR,'Failed to do update the contact.')
                context = {
                'title':'Perbarui Kontak',
                'menu':menu,
                'form':form,
                'contact':contact
                }

            return render(request,'backend/contact/contact_form.html',context,)

        except Exception as err:
            logger.info("Error Update Contact: "+str(err))
            messages.add_message(request,messages.ERROR,'Failed to do update.')

            form = ContactForm(request.POST)

            context = {
                'title':'Perbarui Kontak',
                'menu':menu,
                'form':form,
                'contact':contact
            }

            return render(request,'backend/contact/contact_form.html',context,)
    else:
        if contact:
            form = ContactForm(instance = contact)
        else:
            form = ContactForm()

        context = {
                'title':'Perbarui Kontak',
                'menu':menu,
                'form':form,
                'contact':contact
            }

        return render(request,'backend/contact/contact_form.html',context,)
#END OF CONTACT

#FAQ
@login_required(login_url='/admin/who-login/')
@admin_only
def faq_list(request):
    menu = ['Home','FAQ List']
    title = 'FAQ List'
    faq = FAQ.objects.all().order_by('id')
    context = {
            'title':title,
            'menu':menu,
            'faq':faq
        }

    return render(
        request,
        'backend/faq/faq_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def faq_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Add New FAQ'

    if request.method == 'POST':
        try:
            faqForm = FAQForm(data = request.POST)
            if faqForm.is_valid():
                faq = faqForm.save()
                
                messages.add_message(request,messages.INFO,'New FAQ successfully added.')

                return redirect('/faq/update/edit:'+str(encoding_id(faq.id)))
            else:
                raise forms.ValidationError("FAQ is invalid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'FAQ was not added successfully.')
            faqForm = FAQForm(request.POST)

            context = {
                'title':title,
                'faqForm':faqForm,
            }
    
            return render(request,'backend/faq/faq_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'FAQ was not added successfully.')
            faqForm = FAQForm(request.POST)

            context = {
                'title':title,
                'faqForm':faqForm,
            }
    
            return render(request,'backend/faq/faq_form.html',context)
    else:
        faqForm = FAQForm()

        context = {
            'title':title,
            'faqForm':faqForm,
            }

        return render(request,'backend/faq/faq_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def faq_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit FAQ'

    id = decoding_id(id)
    
    faq = FAQ.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            faqForm = FAQForm(data = request.POST, instance=faq)

            if faqForm.is_valid():
                faq = faqForm.save()
                
                messages.add_message(request,messages.INFO,'FAQ successfully edited.')
                return redirect('/faq/update/edit:'+str(encoding_id(faq.id)))
            else:
                messages.add_message(request,messages.ERROR,+'Failed to edit FAQ (else).')

                context = {
                'title':title,
                'faqForm':faqForm,
                }
    
                return render(request,'backend/faq/faq_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Failed to edit FAQ (except).')
            faqForm = FAQForm(request.POST, instance=faq)

            context = {
                'title':title,
                'faqForm':faqForm,
            }
    
            return render(request,'backend/faq/faq_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            faqForm = FAQForm(instance=faq)

            context = {
                'title':title,
                'faqForm':faqForm,
                }

            return render(request,'backend/faq/faq_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'FAQ successfully deleted.')
            faq.delete()
            return redirect('/faq/list/')
#END OF FAQ

@login_required(login_url='/admin/who-login/')
@admin_only
def tech_list(request):
    assert isinstance(request, HttpRequest)
    title = 'Client'
    menu = ['Jasa', 'Seleksi Jasa']

    tech = Technology.objects.all().order_by('-id')

    context = {
                'title':title,
                'tech':tech,
                }
    return render(request, 'backend/tech/tech_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def tech_add(request):
    assert isinstance(request, HttpRequest)
    title = 'Tech Form'

    if request.method == 'POST':
        #try:
            form = TechnologyForm(request.POST, request.FILES)
            if form.is_valid():
                techform = form.save()
                messages.add_message(request,messages.INFO,'Tech data was successfully added.')

                return redirect('/tech/list/')
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
        form = TechnologyForm()

        context = {
            'title':title,
            'form':form,
            }

        return render(request,'backend/tech/tech_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def tech_update(request, status, id):
    assert isinstance(request, HttpRequest)
    title = 'Edit Tech Info'

    id = decoding_id(id)
    
    tech = Technology.objects.filter(id = id).first()

    if request.method == 'POST':
        try:
            form = TechnologyForm(request.POST, request.FILES, instance=tech)

            if form.is_valid():
                techform = form.save()
                
                messages.add_message(request,messages.INFO,''+techform.name+' successfully edited.')
                return redirect('/tech/list/')
            else:
                messages.add_message(request,messages.ERROR,''+techform.name+' failed to edit.')

                context = {
                'title':title,
                'form':form,
                }
    
                return render(request,'backend/tech/tech_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,''+team.name+' failed to edit (except).')
            form = TechnologyForm(request.POST, request.FILES, instance=tech)

            context = {
                'title':title,
                'form':form,
                'picture':'hidden',
            }
    
            return render(request,'backend/tech/tech_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            form = TechnologyForm(instance=tech)

            context = {
                'title':title,
                'form':form,
                }

            return render(request,'backend/tech/tech_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,''+tech.name+' successfully deleted.')
            tech.delete()
            return redirect('/tech/list/')