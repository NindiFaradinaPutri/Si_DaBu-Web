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
from participant.models import Participant
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

#Set Loggin
import logging
logger = logging.getLogger(__file__)

#CUSTOM
from utils.utils import *
from app.decorators import *
from authentication.forms import *
from authentication.models import *
from event.models import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#Custom

#Error Handling
def handler400(request, *args, **argv):
    return render(request,'error_handler/400.html', context={'menu':['Halaman','Error']}, status=400)

def handler403(request, *args, **argv):
    return render(request,'error_handler/403.html', context={'menu':['Halaman','Error']}, status=403)

def handler404(request, *args, **argv):
    return render(request,'error_handler/404.html', context={'menu':['Halaman','Error']}, status=404)

def handler500(request, *args, **argv):
    return render(request,'error_handler/500.html', context={'menu':['Halaman','Error']}, status=500)

def csrf_failure(request, reason=""):
    return render(request,'error_handler/403_csrf.html', context={'menu':['Halaman','Error']}, status=403)

@transaction.atomic
def admin_signup(request):
    assert isinstance(request, HttpRequest)
    title = 'Registrasi Online'

    if request.method == 'POST':
        with transaction.atomic():
            userForm = PublicSignUpForm(request.POST)
            initProfileForm = InitialProfileForm(request.POST)

            try:
                if userForm.is_valid() and initProfileForm.is_valid():
                    #create user and set activation as false
                    user = userForm.save(commit=False)
                    user.is_user = True
                    user.is_admin = True
                    user.is_active = False
                    user.is_validate = False
                    user.save()

                    #set group
                    user_group, created = Group.objects.get_or_create(name='Admin')
                    user.groups.add(user_group)

                    #create data profile
                    user_profile, created = UserProfile.objects.get_or_create(first_name=initProfileForm.cleaned_data['first_name'], 
                                                                                last_name=initProfileForm.cleaned_data['last_name'],
                                                                                user = user)

                    token, created = Token.objects.get_or_create(user=user)

                    current_site = get_current_site(request)
                    mail_subject = 'Aktivasi Pengguna nganggur.co.id'
                    message = render_to_string('template/registrations/account_activation.html', {
                        'profile': user_profile,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':token,
                    })
                    to_email = userForm.cleaned_data.get('email')
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()

                    context = {
                        'title':title,
                        'user':user,
                        'profile':user_profile
                        }

                    return render(request, 
                                    'template/registrations/account_signup_done.html', 
                                    context)
                else:
                    context = {'userForm':userForm,
                                'initProfileForm':initProfileForm,
                                'title':title}
                    return render(request, 'frontend/signup.html', context)

            except (ValidationError, ValueError) as err:
                messages.add_message(request,messages.ERROR,str(err))
                logger.info("Error Signup Public "+str(err))
                context = {'userForm':userForm,
                            'initProfileForm':initProfileForm,
                            'title':title}
                return render(request, 'frontend/signup.html', context)
            except Exception as err:
                messages.add_message(request,messages.ERROR,str(err))
                logger.info("Error Signup Public "+str(err))
                context = {'userForm':userForm,
                            'initProfileForm':initProfileForm,
                            'title':title}
                return render(request, 'frontend/signup.html', context)
    else:
        userForm = PublicSignUpForm()
        initProfileForm = InitialProfileForm()
        context = {'userForm':userForm,
                    'initProfileForm':initProfileForm,
                    'title':title}
        return render(request, 'frontend/signup.html',context)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserData.objects.get(pk=uid)
        token = Token.objects.filter(key = token).first()

        if user.groups.all()[0].name == 'User':
            if user.is_user == True and token:
                user.is_active = True
                user.is_validate = True
                user.save()
                user_login(request, user)
                return redirect('/user/post/reg/')
        elif user.groups.all()[0].name == 'Staff':
            if user.is_staff == True and token:
                user.is_active = True
                user.is_validate = True
                user.save()
                user_login(request, user)
                return redirect('/staff/post/reg/')
        elif user.groups.all()[0].name == 'Admin':
            if user.is_admin == True and token:
                user.is_active = True
                user.is_validate = False
                user.save()
                user_login(request, user)
                return redirect('/admin/post/reg/')
        elif user.groups.all()[0].name == 'Assessor':
            if user.is_staff == True and token:
                user.is_staff = True
                user.is_validate = True
                user.save()
                user_login(request, user)
                return redirect('/staff/post/reg/')
        else:
            return redirect('/home/')

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        return HttpResponse('Tautan Aktivasi tidak valid!')

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_post_registration(request):
    assert isinstance(request, HttpRequest)
    title = 'Kelengkapan Data Pengguna'
    menu = ['Profil Pengguna','Post Registration']
    
    if request.method == "POST":
        with transaction.atomic():
            if request.user.is_active and request.user.groups.all()[0].name == 'Admin':
                #Data Pengguna
                userForm = UserChangeForm(request.POST, instance = request.user)

                #Profil Pengguna
                user_profile = UserProfile.objects.filter(user_id = request.user.id).first()
                userProfileForm = UserProfileForm(request.POST, instance = user_profile)

                #Data Alamat
                user_address = UserAddress.objects.get_by_user(user_id = request.user.id)
                userAddressForm = UserAddressForm(request.POST, instance=user_address)
                dati2_id = request.POST.get('dati2', None)
                kecamatan_id = request.POST.get('kecamatan', None)
                kelurahan_id = request.POST.get('kelurahan', None)
                userAddressForm.fields['dati2'].queryset = Dati2.objects.filter(id = dati2_id)
                userAddressForm.fields['kecamatan'].queryset = Kecamatan.objects.filter(id = kecamatan_id)
                userAddressForm.fields['kelurahan'].queryset = Kelurahan.objects.filter(id = kelurahan_id)

                #Foto Pengguna
                user_photo = UserPhoto.objects.get_by_user(user_id = request.user.id)
                userPhotoForm = UserPhotoForm(request.POST, request.FILES, instance=user_photo)

                try:
                    if userForm.is_valid():
                        user = userForm.save()
                    else:
                        error = 1
                        context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                        return render(request,'user/post_registration.html',context)
                except (ValidationError, ValueError, Exception) as err:
                    error = 1
                    userForm.add_error(None, str(err))
                    context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                    return render(request,'user/post_registration.html',context)

                try:
                    if userProfileForm.is_valid():
                        user_profile = userProfileForm.save(commit=False)
                        user_profile.user_id = request.user.id
                        user_profile.save()
                    else:
                        error = 2
                        context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                        return render(request,'user/post_registration.html',context)
                except(ValidationError, ValueError, Exception) as err:
                    error = 2
                    userProfileForm.add_error(None, str(err))
                    context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                    return render(request,'user/post_registration.html',context)

                try:
                    if userAddressForm.is_valid():
                        user_address = userAddressForm.save(commit=False)
                        user_address.user = request.user
                        user_address.save()
                    else:
                        error = 3
                        context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                        return render(request,'user/post_registration.html',context)
                except(ValidationError, ValueError, Exception) as err:
                    error = 3
                    userPhotoForm.add_error(None, str(err))
                    context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                    return render(request,'user/post_registration.html',context)

                try:
                    if userPhotoForm.is_valid():
                        if userPhotoForm.cleaned_data.get('information') and userPhotoForm.cleaned_data.get('photo'):
                            user_photo = userPhotoForm.save(commit=False)
                            user_photo.user = request.user
                            user_photo.save()
                        else:
                            error = 4
                            context = {'userForm': userForm, 
                                    'userProfileForm':userProfileForm,
                                    'userAddressForm':userAddressForm,
                                    'userPhotoForm':userPhotoForm,
                                    'menu':menu,
                                    'title':title,
                                    'error':error}
                            return render(request,'user/post_registration.html',context)
                    else:
                        error = 4
                        context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                        return render(request,'user/post_registration.html',context)
                except(ValidationError, ValueError, Exception) as err:
                    error = 4
                    userPhotoForm.add_error(None, str(err))
                    context = {'userForm': userForm, 
                                'userProfileForm':userProfileForm,
                                'userAddressForm':userAddressForm,
                                'userPhotoForm':userPhotoForm,
                                'menu':menu,
                                'title':title,
                                'error':error}
                    return render(request,'user/post_registration.html',context)

                messages.add_message(request,messages.INFO,'Data Profil, Kontak, dan Alamat berhasil ditambahkan.')

                return redirect('/admin/profile/')
    else:
        userForm = UserChangeForm(instance = request.user)

        user_profile = UserProfile.objects.filter(user = request.user).first()
        userProfileForm = UserProfileForm(instance = user_profile)

        user_photo = UserPhoto.objects.get_by_user(user_id = request.user.id)
        if user_photo:
            userPhotoForm = UserPhotoForm(instance=user_photo)
        else:
            userPhotoForm = UserPhotoForm()

        user_address = UserAddress.objects.get_by_user(user_id = request.user.id)
        info_address = {
            'address':user_address
            }
        if user_address:
            userAddressForm = UserAddressForm(instance=user_address,**info_address)
        else:
            userAddressForm = UserAddressForm()

        error = None

        context = {
            'userForm':userForm,
            'menu':menu,
            'userProfileForm':userProfileForm,
            'userPhotoForm':userPhotoForm,
            'userAddressForm':userAddressForm,
            'menu':menu,
            'error':error,
            'title':title,
            }

        return render(request,'user/post_registration.html',context)

@transaction.atomic
def login(request):
    assert isinstance(request, HttpRequest)
    next_page = request.POST.get('next',request.GET.get('next',''))
    title = 'Selamat Datang'
    menu = ['Halaman','Masuk']
    background = 'media/wallpaper/login_1.gif'

    if request.method == "POST": 
        try:
            username = request.POST.get('username', None)

            # ✅ FIX: mapping email → username asli
            user_obj = UserData.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()

            if user_obj:
                request.POST = request.POST.copy()
                request.POST['username'] = user_obj.username

            # 🔽 tetap pakai loginForm seperti semula
            loginForm = LoginForm(data=request.POST)
            # loginForm = LoginForm(data=request.POST)
            # username = request.POST.get('username',None)
            remember_me = request.POST.get('ingat_saya',None)
            token = request.POST.get('unique_code',None)

            #Check Login
            validasi_user = UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).first()
            if not validasi_user:
                return redirect('/home/')
            elif validasi_user:
                is_user = validasi_user.is_user 
                is_admin = validasi_user.is_admin 
                group = validasi_user.groups.all()[0].name
            else:
                is_user = None
                is_admin = None
                group = None
                
            has_access = True

            if not is_admin and not is_user:
                has_access = False
            if not group:
                has_access = False

            if not has_access:
                messages.add_message(request,messages.ERROR,str('Anda tidak memiliki akses'))
                context = {'title':title,'loginForm':loginForm,'background':background}
                return render(request, 'frontend/auth/login.html', context)
            

            if username and token:
                try:
                    if UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).filter(auth_token__key = token).exists():
                        acc_is_active = UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).filter(auth_token__key = token).first()
                        if acc_is_active.is_active == False:
                            acc_is_active.is_active = True
                            acc_is_active.is_validate = True
                            acc_is_active.save()
                     
                            user_login(request, acc_is_active)
                            
                            if group == 'User':
                                return redirect('/user/post/reg/')
                            elif group == 'Admin':
                                return redirect('/admin/post/reg/')

                    else:
                        raise forms.ValidationError(
                            'Kode Token Anda salah. Akun belum diaktifkan. Mohon perhatikan Huruf Besar, kecil dan nomer Token yang tertera.',
                            code='Error',
                        )
                except ValidationError as e:
                    logger.info("Login "+str(e.message))
                    messages.add_message(request,messages.ERROR,str(e.message))
                    context = {'title':title,'loginForm':loginForm,'background':background}
                    return render(request, 'frontend/login.html', context)
                except Exception as e:
                    logger.info("Login "+str(e.args[0]))
                    messages.add_message(request,messages.ERROR,str(e.args[0]))
                    context = {'title':title,'loginForm':loginForm,'background':background}
                    return render(request, 'frontend/login.html', context)
            elif loginForm.is_valid():
                with transaction.atomic():
                    try:
                        user_id = loginForm.user_cache.id

                        user_login(request, loginForm.user_cache)
                        user = request.user

                        ensure_cookies(request)
                        request.session.modified = True

                        data_profile = UserProfile.objects.get_by_user(user_id = user_id)
                        user_address = UserAddress.objects.get_by_user(user_id = user_id)

                        if data_profile:
                            request.session['pengguna_profile'] = data_profile

                        foto = UserPhoto.objects.get_by_user(user_id = user_id)

                        if foto:
                            request.session['pengguna_foto'] = foto.photo.url
                        else:
                            request.session['pengguna_foto'] = 'media/init/avatar.png'

                        if next_page:
                            return HttpResponseRedirect(next_page)
                        if loginForm.user_cache.groups.all()[0].name == 'User':
                            if data_profile and user_address:
                                return redirect('/user/profile/')
                            else:
                                return redirect('/user/post/reg/')
                        elif loginForm.user_cache.groups.all()[0].name == 'Admin':
                            if data_profile and user_address:
                                return redirect('/admin/profile/')
                            else:
                                return redirect('/admin/post/reg/')
                        else:
                            return redirect('/home/')
                    except ValidationError as e:
                        logger.info("Login "+str(e.message))
                        loginForm.add_error(None, str(e.message))
                        context = {'title':title,'loginForm':loginForm,'background':background}
                        return render(request, 'frontend/auth/login.html', context)
                    except Exception as e:
                        logger.info("Login "+str(e.args[0]))
                        loginForm.add_error(None, str(e.args[0]))
                        context = {'title':title,'loginForm':loginForm,'background':background}
                        return render(request, 'frontend/auth/login.html', context)
            else:
                messages.add_message(request,messages.ERROR,str('Username atau password tidak dikenali'))
                loginForm = LoginForm(request.POST)
                context = {'title':title,'loginForm':loginForm,'background':background}
                return render(request, 'frontend/auth/login.html', context)
        except ValidationError as e:
                logger.info("Login "+str(e.message))
                messages.add_message(request,messages.ERROR,str(e.message))
                context = {'title':title,'loginForm':loginForm,'background':background}
                return render(request, 'frontend/auth/login.html', context)
        except Exception as e:
            logger.info("Login "+str(e.args[0]))
            messages.add_message(request,messages.ERROR,str(e.args[0]))
            context = {'title':title,'loginForm':loginForm,'background':background}
            return render(request, 'frontend/auth/login.html', context)
    else:
        loginForm = LoginForm()
        
        context = {'title':title,
                   'menu':menu,
                   'loginForm':loginForm,
                   'background':background}
        return render(request, 'frontend/auth/login.html', context)
    

# @transaction.atomic
# def login(request):
#     assert isinstance(request, HttpRequest)
#     next_page = request.POST.get('next',request.GET.get('next',''))
#     title = 'Selamat Datang'
#     menu = ['Halaman','Masuk']
#     background = 'media/wallpaper/login_1.gif'

#     if request.method == "POST": 
#         try:
#             username = request.POST.get('username', None)

#             # ✅ FIX: mapping email → username asli
#             user_obj = UserData.objects.filter(
#                 Q(username__iexact=username) | Q(email__iexact=username)
#             ).first()

#             if user_obj:
#                 request.POST = request.POST.copy()
#                 request.POST['username'] = user_obj.username

#             # 🔽 tetap pakai loginForm seperti semula
#             loginForm = LoginForm(data=request.POST)

#             remember_me = request.POST.get('ingat_saya',None)
#             token = request.POST.get('unique_code',None)

#             #Check Login
#             validasi_user = UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).first()
#             if not validasi_user:
#                 return redirect('/home/')
#             elif validasi_user:
#                 is_user = validasi_user.is_user 
#                 is_admin = validasi_user.is_admin 
#                 group = validasi_user.groups.all()[0].name
#             else:
#                 is_user = None
#                 is_admin = None
#                 group = None
                
#             has_access = True

#             if not is_admin and not is_user:
#                 has_access = False
#             if not group:
#                 has_access = False

#             if not has_access:
#                 messages.add_message(request,messages.ERROR,str('Anda tidak memiliki akses'))
#                 context = {'title':title,'loginForm':loginForm,'background':background}
#                 return render(request, 'frontend/auth/login.html', context)
            

#             if username and token:
#                 try:
#                     if UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).filter(auth_token__key = token).exists():
#                         acc_is_active = UserData.objects.filter(Q(username__iexact = username) | Q(email__iexact = username)).filter(auth_token__key = token).first()
#                         if acc_is_active.is_active == False:
#                             acc_is_active.is_active = True
#                             acc_is_active.is_validate = True
#                             acc_is_active.save()
                     
#                             user_login(request, acc_is_active)
                            
#                             if group == 'User':
#                                 return redirect('/user/post/reg/')
#                             elif group == 'Admin':
#                                 return redirect('/admin/post/reg/')

#                     else:
#                         raise forms.ValidationError(
#                             'Kode Token Anda salah. Akun belum diaktifkan. Mohon perhatikan Huruf Besar, kecil dan nomer Token yang tertera.',
#                             code='Error',
#                         )
#                 except ValidationError as e:
#                     logger.info("Login "+str(e.message))
#                     messages.add_message(request,messages.ERROR,str(e.message))
#                     context = {'title':title,'loginForm':loginForm,'background':background}
#                     return render(request, 'frontend/login.html', context)
#                 except Exception as e:
#                     logger.info("Login "+str(e.args[0]))
#                     messages.add_message(request,messages.ERROR,str(e.args[0]))
#                     context = {'title':title,'loginForm':loginForm,'background':background}
#                     return render(request, 'frontend/login.html', context)

#             elif loginForm.is_valid():
#                 with transaction.atomic():
#                     try:
#                         user_id = loginForm.user_cache.id

#                         user_login(request, loginForm.user_cache)
#                         user = request.user

#                         ensure_cookies(request)
#                         request.session.modified = True

#                         data_profile = UserProfile.objects.get_by_user(user_id = user_id)
#                         user_address = UserAddress.objects.get_by_user(user_id = user_id)

#                         if data_profile:
#                             request.session['pengguna_profile'] = data_profile

#                         foto = UserPhoto.objects.get_by_user(user_id = user_id)

#                         if foto:
#                             request.session['pengguna_foto'] = foto.photo.url
#                         else:
#                             request.session['pengguna_foto'] = 'media/init/avatar.png'

#                         if next_page:
#                             return HttpResponseRedirect(next_page)

#                         if loginForm.user_cache.groups.all()[0].name == 'User':
#                             if data_profile and user_address:
#                                 return redirect('/user/profile/')
#                             else:
#                                 return redirect('/user/post/reg/')
#                         elif loginForm.user_cache.groups.all()[0].name == 'Admin':
#                             if data_profile and user_address:
#                                 return redirect('/admin/profile/')
#                             else:
#                                 return redirect('/admin/post/reg/')
#                         else:
#                             return redirect('/home/')

#                     except ValidationError as e:
#                         logger.info("Login "+str(e.message))
#                         loginForm.add_error(None, str(e.message))
#                         context = {'title':title,'loginForm':loginForm,'background':background}
#                         return render(request, 'frontend/auth/login.html', context)

#                     except Exception as e:
#                         logger.info("Login "+str(e.args[0]))
#                         loginForm.add_error(None, str(e.args[0]))
#                         context = {'title':title,'loginForm':loginForm,'background':background}
#                         return render(request, 'frontend/auth/login.html', context)

#             else:
#                 messages.add_message(request,messages.ERROR,str('Username atau password tidak dikenali'))
#                 loginForm = LoginForm(request.POST)
#                 context = {'title':title,'loginForm':loginForm,'background':background}
#                 return render(request, 'frontend/auth/login.html', context)

#         except ValidationError as e:
#             logger.info("Login "+str(e.message))
#             messages.add_message(request,messages.ERROR,str(e.message))
#             context = {'title':title,'loginForm':loginForm,'background':background}
#             return render(request, 'frontend/auth/login.html', context)

#         except Exception as e:
#             logger.info("Login "+str(e.args[0]))
#             messages.add_message(request,messages.ERROR,str(e.args[0]))
#             context = {'title':title,'loginForm':loginForm,'background':background}
#             return render(request, 'frontend/auth/login.html', context)

#     else:
#         loginForm = LoginForm()
        
#         context = {
#             'title':title,
#             'menu':menu,
#             'loginForm':loginForm,
#             'background':background
#         }
#         return render(request, 'frontend/auth/login.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_profile(request):
    assert isinstance(request, HttpRequest)
    title = 'Profil Admin'
    menu = ['Profil Admin','Profil']

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        user_photo = UserPhoto.objects.get_by_user(user_id=request.user.id)
        user_address = UserAddress.objects.get_by_user(user_id=request.user.id)
        user_description = UserDescription.objects.filter(user_id=request.user.id).first()

        # =========================
        # EVENT STATS (TIDAK DIUBAH LOGICNYA)
        # =========================
        now = timezone.now()
        today = now.date()
        current_time = now.time()

        total_events = Event.objects.count()

        upcoming_events = Event.objects.filter(
            Q(date__gt=today) |
            Q(date=today, time__gte=current_time)
        )

        upcoming_events_count = upcoming_events.count()

        registered_count = Participant.objects.filter(
            status_user_id__status_name="Register"
        ).count()

        present_count = Participant.objects.filter(
            status_user_id__status_name="Present"
        ).count()

        checkin_rate = 0
        if registered_count > 0:
            checkin_rate = round((present_count / registered_count) * 100, 1)

        events_qs = Event.objects.prefetch_related(
            'eventphoto_set'
        ).all()
        # =========================
        # EVENT LIST (TAMBAHAN SAJA, NON-INTRUSIVE)
        # =========================
        events = []

        for event in events_qs:

            # =========================
            # STATUS LOGIC INLINE
            # =========================
            status = "EVENT FINISHED"
            badge_class = "bg-secondary text-white"

            if event.date > today:
                status = "INCOMING"
                badge_class = "bg-warning text-dark"

            elif event.date == today:
                if event.time:
                    if event.time <= current_time:
                        status = "LIVE MANAGEMENT"
                        badge_class = "bg-danger text-white"
                    else:
                        status = "INCOMING"
                        badge_class = "bg-warning text-dark"
                else:
                    status = "LIVE MANAGEMENT"
                    badge_class = "bg-danger text-white"

            # =========================
            # ATTACH ATTRIBUTE KE OBJECT
            # (tanpa append dict baru)
            # =========================
            event.status = status
            event.badge_class = badge_class

            events.append(event)

        context = {
            'title': title,
            'menu': menu,
            'user': request.user,
            'user_profile': user_profile,
            'user_photo': user_photo,
            'user_address': user_address,
            'user_description': user_description,
            'time': datetime.now().time(),

            # STATS (UNCHANGED)
            'total_events': total_events,
            'upcoming_events_count': upcoming_events_count,
            'registered_count': registered_count,
            'checkin_rate': checkin_rate,

            # EVENTS (BARU TAMBAHAN)
            'events': events,
        }

        return render(request, 'backend/profile/user_profile.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_profile_update(request):
    assert isinstance(request, HttpRequest)
    title = 'Update Profil Pengguna'
    menu = ['Profil Pengguna','Ubah Profil']

    if request.method == 'POST':
        #Initiate Parameter
        user = request.user
        userForm = UserChangeForm(request.POST, instance=user)

        user_profile = UserProfile.objects.get_by_user(user_id = request.user.id)
        userProfileForm = UserProfileForm(request.POST, instance = user_profile)

        user_photo = UserPhoto.objects.get_by_user(user_id = user.id)
        userPhotoForm = UserPhotoForm(request.POST, request.FILES, instance=user_photo)

        user_address = UserAddress.objects.get_by_user(user_id = user.id)
        userAddressForm = UserAddressForm(request.POST, instance=user_address)
        try:
            if 'data_user' in request.POST:
                if userForm.is_valid():
                    user = userForm.save()
                    messages.add_message(request,messages.INFO,'Data kontak telah diperbarui')
                    return redirect('/admin/profile/update/')
                else:
                    messages.add_message(request,messages.ERROR,'Data kontak tidak diperbarui')
                    context = {'userForm': userForm, 
                           'userProfileForm':userProfileForm,
                           'userPhotoForm':userPhotoForm,
                           'userAddressForm':userAddressForm,
                           'menu':menu,
                           'title':title}
                    return render(request, 'backend-admin/profile_update.html',context)
                
            elif 'data_profile' in request.POST:
                if userProfileForm.is_valid():
                    profile = userProfileForm.save()
                    profile.user = user
                    profile.save()
                    messages.add_message(request,messages.INFO,'Data profil telah diperbarui')
                    return redirect('/admin/profile/update/')
                else:
                    messages.add_message(request,messages.ERROR,'Data profil tidak diperbarui')
                    context = {'userForm': userForm, 
                           'userProfileForm':userProfileForm,
                           'userPhotoForm':userPhotoForm,
                           'userAddressForm':userAddressForm,
                           'menu':menu,
                           'title':title}
                    return render(request, 'backend-admin/profile_update.html',context)

            elif 'data_address' in request.POST:
                dati2_id = request.POST.get('dati2', None)
                kecamatan_id = request.POST.get('kecamatan', None)
                kelurahan_id = request.POST.get('kelurahan', None)
                userAddressForm.fields['dati2'].queryset = Dati2.objects.filter(id = dati2_id)
                userAddressForm.fields['kecamatan'].queryset = Kecamatan.objects.filter(id = kecamatan_id)
                userAddressForm.fields['kelurahan'].queryset = Kelurahan.objects.filter(id = kelurahan_id)
                if userAddressForm.is_valid():
                    address = userAddressForm.save(commit=False)
                    address.user = user
                    address.save()

                    messages.add_message(request,messages.INFO,'Data alamat telah diperbarui')
                    return redirect('/admin/profile/update/')
                else:
                    messages.add_message(request,messages.ERROR,'Data alamat tidak diperbarui')
                    context = {'userForm': userForm, 
                           'userProfileForm':userProfileForm,
                           'userPhotoForm':userPhotoForm,
                           'userAddressForm':userAddressForm,
                           'menu':menu,
                           'title':title}
                    return render(request, 'backend-admin/profile_update.html',context)

            elif 'data_photo' in request.POST:
                if userPhotoForm.is_valid():
                    photo = userPhotoForm.save(commit=False)
                    photo.user = user
                    photo.save()

                    messages.add_message(request,messages.INFO,'Foto telah diperbarui')
                    return redirect('/admin/profile/update/')
                else:
                    messages.add_message(request,messages.ERROR,'Foto tidak diperbarui')
                    context = {'userForm': userForm, 
                           'userProfileForm':userProfileForm,
                           'userPhotoForm':userPhotoForm,
                           'userAddressForm':userAddressForm,
                           'menu':menu,
                           'title':title}
                    return render(request, 'backend-admin/profile_update.html',context)

        except Exception as err:
            messages.add_message(request,messages.ERROR,'Terjadi kesalahan dalam pengisian:'+str(err.args[-1]))
            context = {'userForm': userForm, 
                        'userProfileForm':userProfileForm,
                        'userPhotoForm':userPhotoForm,
                        'userAddressForm':userAddressForm,
                        'menu':menu,
                        'title':title}
            return render(request,'backend-admin/profile_update.html',context)
    else:
        #Initiate Parameter
        user = request.user
        userForm = UserChangeForm(instance=user)

        user_profile = UserProfile.objects.get_by_user(user_id = request.user.id)
        userProfileForm = UserProfileForm(instance = user_profile)

        user_photo = UserPhoto.objects.get_by_user(user_id = user.id)
        if user_photo:
            userPhotoForm = UserPhotoForm(instance=user_photo)
        else:
            userPhotoForm = UserPhotoForm()

        user_address = UserAddress.objects.get_by_user(user_id = user.id)
        info_address = {
                'address':user_address
                }
        if user_address:
                userAddressForm = UserAddressForm(instance=user_address,**info_address)
        else:
            userAddressForm = UserAddressForm()
        
        context = {
            'title':title,
            'menu':menu,
            'userForm':userForm,
            'userProfileForm':userProfileForm,
            'userPhotoForm':userPhotoForm,
            'userAddressForm':userAddressForm,
            }

        return render(request, 'user/profile_update.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_password_change(request):
    assert isinstance(request, HttpRequest)
    title = 'Ubah Password'
    menu = ['Profil Pengguna','Ubah Password']

    user = request.user

    if request.method == 'POST':
        user = request.user
        changePasswordForm = ChangePasswordForm(request.POST, user=request.user, instance = user)

        if changePasswordForm.is_valid():
            try:
                user = changePasswordForm.save()
                
                messages.add_message(request,messages.SUCCESS, 'Password berhasil diubah. Anda harus login kembali');
                auth_logout(request)
                return redirect('/login/')

            except ValidationError as e:
                changePasswordForm.add_error(None, str(e.message))
                context = {'title':title,'menu':menu,'changePasswordForm':changePasswordForm}
                return render(request, 'template/registrations/password_change_form.html', context)
            except Exception as e:
                changePasswordForm.add_error(None, str(e.args[-1]))
                context = {'title':title,'menu':menu,'changePasswordForm':changePasswordForm}
                return render(request, 'template/registrations/password_change_form.html', context)
        else:
            context = {'title':title,'menu':menu,'changePasswordForm':changePasswordForm}
            return render(request, 'template/registrations/password_change_form.html', context)
    else:
        changePasswordForm = ChangePasswordForm()

        context = {'title':title,'menu':menu,'changePasswordForm':changePasswordForm}
        return render(request, 'template/registrations/password_change_form.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_delete(request, id):
    user = UserData.objects.get(id = id)
    messages.add_message(request,messages.WARNING,'Data User '+user.username+' berhasil dihapus.')
    user.delete()
    return redirect('/admin/list/')

@login_required(login_url='/admin/who-login/')
@admin_only
def admin_list(request):
    assert isinstance(request, HttpRequest)
    title = 'List Admin'
    menu = ['Kelola Pengguna', 'List Pengguna']

    queryset = UserProfile.objects.filter(user__groups__name = 'Admin')

    profil_filter = UserFilter(request.POST, queryset=queryset)

    page = request.GET.get('page',1)

    paginator = Paginator(profil_filter.qs.order_by('id'), per_page=16)

    try:
        profil_user_query = paginator.page(page)
    except PageNotAnInteger:
        profil_user_query = paginator.page(1)
    except EmptyPage:
        profil_user_query = paginator.page(paginator.num_pages)

    context = {'title':title, 
               'profiles':profil_user_query,
               'jenis': 'admin',
               'profil_filter': profil_filter
               }
    return render(request,'backend-admin/user/user_list.html',context)

