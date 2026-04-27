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

#Set Logg
import logging
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
from kegiatan.models import *
from kegiatan.forms import *
from team.models import *
from information.models import *
from information.forms import *
from app.crons import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

current_tzinfo = timezone.get_current_timezone()

def kegiatan(request):
    assert isinstance(request, HttpRequest)
    menu = ['Beranda','Kegiatan']
    title = 'Kegiatan'

    kegiatan_query = Kegiatan.objects.all().order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(kegiatan_query, per_page=9)

    try:
        kegiatan = paginator.page(page)
    except PageNotAnInteger:
        kegiatan = paginator.page(1)
    except EmptyPage:
        kegiatan = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'kegiatan':kegiatan,
        'data':'all',
        }

    return render(
        request,
        'frontend/kegiatan/kegiatan.html',
        context,
    )

def kegiatan_category(request,category):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Kegiatan category']
    title = 'Kegiatan category'

    if category == 'all':
        kegiatan_query = Kegiatan.objects.all().order_by('-id')
    elif category == 'photo':
        kegiatan_query = Kegiatan.objects.exclude(foto = '').order_by('-id')
    elif category == 'video':
        kegiatan_query = Kegiatan.objects.exclude(video = '').order_by('-id')
    elif category == 'link':
        kegiatan_query = Kegiatan.objects.filter(link__isnull=False).order_by('-id')

    page = request.GET.get('page',1)

    paginator = Paginator(kegiatan_query, per_page=9)

    try:
        kegiatan = paginator.page(page)
    except PageNotAnInteger:
        kegiatan = paginator.page(1)
    except EmptyPage:
        kegiatan = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'kegiatan':kegiatan,
        'data':category,
        }

    return render(
        request,
        'frontend/kegiatan/kegiatan.html',
        context,
    )

# @login_required(login_url='/admin/who-login/')
# @admin_only
def kegiatan_list(request):
    menu = ['Home','Kegiatan List']
    title = 'Kegiatan'
    kegiatan = Kegiatan.objects.all().order_by('-id')
    context = {
            'title':title,
            'menu':menu,
            'kegiatan':kegiatan
        }

    return render(
        request,
        'backend/kegiatan/kegiatan_list.html',
        context,
    )

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Add Item to Kegiatan']
    title = 'Add Item to Kegiatan'

    if request.method == 'POST':
        try:
            kegiatanForm = KegiatanForm(request.POST,request.FILES)
            video = request.FILES.get('video',None)
            photo = request.FILES.get('foto',None)

            if (video and photo):
                messages.add_message(request,messages.ERROR,'Can not upload videos / photos / links at the same time.')
                kegiatanForm = KegiatanForm(request.POST,request.FILES)

                context = {
                    'title':title,
                    'kegiatanForm':kegiatanForm
                }
    
                return render(request,'backend/kegiatan/kegiatan_form.html',context)
            else:
                if kegiatanForm.is_valid():
                    item = kegiatanForm.save()
                    messages.add_message(request,messages.SUCCESS,'Item successfully added to kegiatan.')

                    return redirect('/kegiatan/update/edit:'+str(encoding_id(item.id))+'/')
                else: 
                    raise ValidationError('Form tidak lengkap ');
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Error adding item to the kegiatan.')
            kegiatanForm = KegiatanForm(request.POST,request.FILES)

            context = {
                'title':title,
                'kegiatanForm':kegiatanForm
            }
    
            return render(request,'backend/kegiatan/kegiatan_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Error adding item to the kegiatan.')
            kegiatanForm = KegiatanForm(request.POST,request.FILES)

            context = {
                'title':title,
                'kegiatanForm':kegiatanForm
            }
    
            return render(request,'backend/kegiatan/kegiatan_form.html',context)
    else:
        kegiatanForm = KegiatanForm()

        context = {
            'title':title,
            'kegiatanForm':kegiatanForm
        }

        return render(request,'backend/kegiatan/kegiatan_form.html',context)

# @login_required(login_url='/admin/who-login/')
# @admin_only
def kegiatan_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit Item']
    title = 'Edit Item'
    id = decoding_id(id)
    kegiatan = Kegiatan.objects.filter(id=id).first()

    if request.method == 'POST':
        with transaction.atomic():
            kegiatanForm = KegiatanForm(data = request.POST, files = request.FILES, instance=kegiatan)
            video = request.FILES.get('video',None)
            photo = request.FILES.get('foto',None)
            try:
                if (video and photo):
                    messages.add_message(request,messages.ERROR,'Can not upload videos / photos / links at the same time.')
                    kegiatanForm = KegiatanForm(request.POST,instance=kegiatan)

                    context = {
                        'title':title,
                        'kegiatanForm':kegiatanForm,
                    }
    
                    return render(request,'backend/kegiatan/kegiatan_form.html',context)
                else:
                    if kegiatanForm.is_valid():
                        item = kegiatanForm.save()
                        messages.add_message(request,messages.SUCCESS,'Item successfully added to kegiatan.')

                        return redirect('/kegiatan/update/edit:'+str(encoding_id(item.id))+'/')
                    else:
                        raise forms.ValidationError("Item is invalid.")

            except ValidationError as e:
                messages.add_message(request,messages.ERROR,'Error editing the item.')
                logger.error('Error editing the item '+str(e))
                kegiatanForm = KegiatanForm(request.POST,instance=kegiatan)

                context = {
                    'title':title,
                    'kegiatanForm':kegiatanForm,
                }
    
                return render(request,'backend/kegiatan/kegiatan_form.html',context)
            except Exception as e:
                messages.add_message(request,messages.ERROR,'Error editing the item.')
                logger.error('Error editing the item '+str(e))
                kegiatanForm = KegiatanForm(request.POST,instance=kegiatan)

                context = {
                    'title':title,
                    'kegiatanForm':kegiatanForm,
                }
    
                return render(request,'backend/kegiatan/kegiatan_form.html',context)

    elif request.method == 'GET':
        if status == 'edit':
            kegiatanForm = KegiatanForm(instance=kegiatan)

            context = {
                'title':title,
                'kegiatanForm':kegiatanForm,
                }

            return render(request,'backend/kegiatan/kegiatan_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,'Item successfully deleted.')
            kegiatan.delete()
            return redirect('/kegiatan/list/')
        
#kegiatan transaksi

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_list(request):
    menu = ['Home','COA Group List']
    title = 'COA Group List'

    coa_group = ChartOfAccountsGroup.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'coa_group':coa_group}

    return render(request, 'backend/kegiatan/coa_group_list_zakat.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Add New COA Group']
    title = 'Add New COA Group'

    if request.method == 'POST':
        try:
            coaGroupForm = COAGroupForms(data = request.POST)
            if coaGroupForm.is_valid():
                coa = coaGroupForm.save()
                
                messages.add_message(request,messages.INFO,coa.group_name +' successfully added.')

                return redirect('/coa/group/zakat/')
            else:
                raise forms.ValidationError("COA Group tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'COA Group tidak berhasil ditambahkan.')
            coaGroupForm = COAGroupForms(data = request.POST)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA Group tidak berhasil ditambahkan.')
            coaGroupForm = COAGroupForms(data = request.POST)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)
    else:
        coaGroupForm = COAGroupForms()

        context = {
            'title':title,
            'coaGroupForm':coaGroupForm,
            }

        return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit COA Group']
    title = 'Edit New COA Group'

    id = decoding_id(id)
    
    coa_group = ChartOfAccountsGroup.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            coaGroupForm = COAGroupForms(data = request.POST, instance=coa_group)

            if coaGroupForm.is_valid():
                coa_group = coaGroupForm.save()
                
                messages.add_message(request,messages.INFO,coa_group.group_name +' berhasil diedit.')
                return redirect('/coa/group/zakat')
            else:
                messages.add_message(request,messages.ERROR,coa_group.group_name+' gagal diupdate.')

                context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
                }
    
                return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,coa_group.group_name +' gagal diupdate.')
            coaGroupForm = COAGroupForms(instance=coa_group)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            coaGroupForm = COAGroupForms(instance=coa_group)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
                }

            return render(request,'backend/kegiatan/coa_group_form_zakat.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,coa_group.group_name+' berhasil dihapus.')
            coa_group.delete()
            return redirect('/coa/group/zakat/')

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_list(request):
    menu = ['Home','COA List']
    title = 'COA List'

    coa = ChartOfAccounts.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'coa':coa}

    return render(request, 'backend/kegiatan/coa_list_zakat.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah COA Baru']
    title = 'Tambah COA Baru'

    if request.method == 'POST':
        try:
            coaForm = COAForms(data = request.POST)
            if coaForm.is_valid():
                coa = coaForm.save()
                
                messages.add_message(request,messages.INFO,coa.account_name +' successfully added.')

                return redirect('/coa/zakat/')
            else:
                raise forms.ValidationError("COA tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            coaForm = COAForms(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/kegiatan/coa_form_zakat.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            coaForm = COAForms(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/kegiatan/coa_form_zakat.html',context)
    else:
        coaForm = COAForms()

        context = {
            'title':title,
            'menu':menu,
            'coaForm':coaForm,
            }

        return render(request,'backend/kegiatan/coa_form_zakat.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit COA']
    title = 'Edit New COA'

    id = decoding_id(id)
    
    coa = ChartOfAccounts.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            coaForm = COAForms(data = request.POST, instance=coa)

            if coaForm.is_valid():
                coa = coaForm.save()
                
                messages.add_message(request,messages.INFO,coa.account_name +' berhasil diedit.')
                return redirect('/coa/edit:'+str(encoding_id(coa.id)))
            else:
                messages.add_message(request,messages.ERROR,coa.account_name+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
                }
    
                return render(request,'backend/kegiatan/coa_form_zakat.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,coa.account_name+' gagal diupdate.')
            coaForm = COAForms(instance=coa)

            context = {
                'title':title,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/kegiatan/coa_form_zakat.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            coaForm = COAForms(instance=coa)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
                }

            return render(request,'backend/kegiatan/coa_form_zakat.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,coa.account_name +' berhasil dihapus.')
            coa.delete()
            return redirect('/coa/zakat/')

@login_required(login_url='/admin/who-login/')
@admin_only
def show_kegiatan_transaksi_list(request):
    menu = ['Home','Kegiatan Transaksi']
    title = 'Kegiatan Transaksi'

    gl = KegiatanAkuntasi.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'gl':gl}

    return render(request, 'backend/kegiatan/general_ledger_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def show_kegiatan_transaksi_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Transaksi Baru']
    title = 'Transaksi Baru'

    if request.method == 'POST':
        try:
            glForm = KegiatanAkuntasiForm(data = request.POST)
            glAttachmentForm = KegiatanAkuntasiAttachmentForm(data = request.POST, files=request.FILES)

            if glForm.is_valid() and glAttachmentForm.is_valid():
                gl = glForm.save()

                glAttachment = glAttachmentForm.save(commit=False)
                glAttachment.general_ledger = gl
                glAttachment.save()
                
                messages.add_message(request,messages.INFO,gl.transaction +' successfully added.')

                return redirect('/gl/')
            else:
                raise forms.ValidationError("Transaksi tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Transaksi tidak berhasil ditambahkan.')
            glForm = KegiatanAkuntasiForm(data = request.POST)
            glAttachmentForm = KegiatanAkuntasiAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
            }
    
            return render(request,'backend/kegiatan/general_ledger_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            glForm = KegiatanAkuntasiForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
            }
    
            return render(request,'backend/kegiatan/general_ledger_form.html',context)
    else:
        glForm = KegiatanAkuntasiForm()
        glAttachmentForm = KegiatanAkuntasiAttachmentForm()

        context = {
            'title':title,
            'menu':menu,
            'glForm':glForm,
            'glAttachmentForm':glAttachmentForm,
            }

        return render(request,'backend/kegiatan/general_ledger_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def show_kegiatan_transaksi_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Transaksi']
    title = 'Ubah Transaksi'

    id = decoding_id(id)
    
    gl = KegiatanAkuntasi.objects.filter(id=id).first()
    gl_attachment = KegiatanAkuntasiAttachment.objects.filter(general_ledger = gl).first()

    if request.method == 'POST':
        try:
            glForm = KegiatanAkuntasiForm(data = request.POST, instance=gl)
            glAttachmentForm = KegiatanAkuntasiAttachmentForm(data = request.POST, files=request.FILES, instance = gl_attachment)

            if glForm.is_valid():
                gl = glForm.save()

                glAttachment = glAttachmentForm.save(commit=False)
                glAttachment.general_ledger = gl
                glAttachment.save()
                
                messages.add_message(request,messages.INFO,gl.transaction+' berhasil diedit.')
                return redirect('/gl/')
            else:
                messages.add_message(request,messages.ERROR,gl.transaction+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
                }
    
                return render(request,'backend/kegiatan/general_ledger_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,gl.transaction+' gagal diupdate.')
            glForm = KegiatanAkuntasiForm(data = request.POST, instance=gl)
            glAttachmentForm = KegiatanAkuntasiAttachmentForm(data = request.POST, files=request.FILES, instance = gl_attachment)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
            }
    
            return render(request,'backend/kegiatan/general_ledger_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            glForm = KegiatanAkuntasiForm(instance=gl)
            glAttachmentForm = KegiatanAkuntasiAttachmentForm(instance = gl_attachment)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
                }

            return render(request,'backend/kegiatan/general_ledger_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,gl.transaction+' berhasil dihapus.')
            gl.delete()
            return redirect('/gl/')

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_transaksi_list(request):
    menu = ['Home','Buku Besar']
    title = 'Buku Besar'

    gl = KegiatanAkuntasi.objects.all().order_by('order_no')
    context = {
        'title':title,
        'menu':menu,
        'gl':gl,
        }

    return render(request, 'backend/kegiatan/transaction_table_zakat.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
@transaction.atomic
def kegiatan_transaksi_update(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah/Ubah Transaksi']
    title = 'Tambah/Ubah Transaksi'
    
    transaction_count = 0
    last_saldo = KegiatanJurnal.objects.filter(status='Saldo Akhir', is_active = True).last() 
    if last_saldo:
        selected_row = KegiatanAkuntasi.objects.filter(order_no = last_saldo.gl_order_no).last()
        n_count = last_saldo.gl_order_no
    else: 
        selected_row = None
        n_count = 0
        #n_count = KegiatanAkuntasi.objects.filter(id__lte  = selected_row.id).count()
        
    if(last_saldo):
        last_total = last_saldo.balance
    else:
        last_total = 0
    gl_formset = modelformset_factory(KegiatanAkuntasi,form=KegiatanAkuntasiForm, extra=transaction_count,min_num=1,max_num=1200)

    table_head = mark_safe(  "<th width='5%'>No</th>"
					    "<th width='10%' data-priority='1'>Tanggal</th>"
						"<th width='10%'>Akun</th>"
                        "<th width='15%'>Nama</th>"
						"<th width='15%' data-priority='2'>Informasi</th>"
                        "<th width='10%' data-priority='4'>Beras</th>"
						"<th width='10%' data-priority='5'>Debet</th>"
						"<th width='10%' data-priority='6'>Kredit</th>"
						"<th width='10%' data-priority='3'>Saldo</th>"
						"<th width='5%'>Aksi</th>")

    if request.method == 'POST':
        try:
            glForm = gl_formset(request.POST, queryset=KegiatanAkuntasi.objects.all().order_by('date'), prefix='gl')

            if glForm.is_valid():
                #check date difungsikan untuk mengetahui iterasi
                check_date = None
                reorder = False
                for index, gl in enumerate(glForm):
                    index += 1
                    if gl.cleaned_data.get('id'):
                        gl_item = gl.save()
                        gl_item.order_no = index
                        gl_item.save()

                        #jika tidak butuh reorder terus lanjut, jika butuh order, pilih tanggal terkecil
                        if not reorder:
                            check_date = gl_item.date
                    elif not gl.cleaned_data.get('id'):
                        gl_item = gl.save()
                        gl_item.order_no = index
                        gl_item.save()

                        #jika tidak butuh reorder terus lanjut, jika butuh order, pilih tanggal terkecil
                        if gl_item.date:
                            check_date = gl_item.date
                            reorder = True
                        elif not reorder:
                            check_date = gl_item.date

                if reorder:
                    #clear week journal
                    # del_journal = KegiatanJurnal.objects.filter(date__date__gte = check_date).delete()

                    #reorder and calculate
                    gl_last_order = KegiatanAkuntasi.objects.filter(date__date__lt = check_date).order_by('order_no','date').last()
                    if gl_last_order:
                        last_order = gl_last_order.order_no
                        last_balance = gl_last_order.balance
                    else:
                        last_order = 0
                        last_balance = 0

                    gl_list = KegiatanAkuntasi.objects.filter(date__date__gte = check_date).order_by('date','order_no')
                    for gl in gl_list:
                        last_order += 1
                        gl.order_no = last_order

                        if gl.debet:
                            last_balance += gl.debet
                            gl.balance = last_balance
                        elif gl.credit:
                            last_balance -= gl.credit
                            gl.balance = last_balance
                        
                        gl.save()

                #ambil last checked point
                KegiatanAkuntasi.objects.update(last_checked=False)
                last_checked = KegiatanAkuntasi.objects.last()
                last_checked.last_checked = True
                last_checked.save()
                        
                update_journal_week()
                messages.add_message(request,messages.INFO,'GL berhasil diupdate.')
                return redirect('/transaction/zakat/')
            else:
                messages.add_message(request,messages.ERROR,'GL gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'table_head':table_head,
                'last_total':last_total,
                'n_count':n_count,
                }
                
    
                return render(request,'backend/kegiatan/transaction_table_zakat_update.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'GL gagal diupdate.')
            glForm = KegiatanAkuntasiForm(data = request.POST, instance=gl)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'table_head':table_head,
                'last_total':last_total,
                'n_count':n_count,
            }
    
            return render(request,'backend/kegiatan/transaction_table_zakat_update.html',context)
    else:
        glForm = gl_formset(queryset=KegiatanAkuntasi.objects.all().order_by('order_no'), prefix='gl')
        
        context = {
            'title':title,
            'menu':menu,
            'glForm':glForm,
            'table_head':table_head,
            'last_total':last_total,
            'n_count':n_count,
            }

        return render(request,'backend/kegiatan/transaction_table_zakat_update.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_jurnal_list(request):
    menu = ['Home','Jurnal Mingguan']
    title = 'Jurnal Mingguan'

    week_journal = KegiatanJurnal.objects.filter(is_active = True).order_by('date')
    context = {
        'title':title,
        'menu':menu,
        'week_journal':week_journal,
        }

    return render(request, 'backend/kegiatan/week_journal.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_jurnal_update(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Validasi jurnal']
    title = 'Validasi Jurnal'
    
    journal_count = 0
    last_saldo = KegiatanJurnal.objects.filter(status='Saldo Akhir', is_active = True).last()
    if(last_saldo):
        last_total = last_saldo.balance
    else:
        last_total = 0

    journal_formset = modelformset_factory(KegiatanJurnal,form=KegiatanJurnalForm, extra=journal_count,min_num=1,max_num=300)

    table_head = mark_safe(  
                        "<th width='5%'>No</th>"
                        "<th width='5%' data-priority='3'>Aktif?</th>"
					    "<th width='15%' data-priority='1'>Tanggal</th>"
						"<th width='10%'>Akun</th>"
						"<th width='25%' data-priority='2'>Transaksi</th>"
                        "<th width='10%' data-priority='3'>Status</th>"
						"<th width='10%' data-priority='4'>Debet</th>"
						"<th width='10%' data-priority='5'>Kredit</th>"
                        "<th width='10%' data-priority='3'>Saldo</th>"
						"<th width='10%'>Aksi</th>")

    if request.method == 'POST':
        try:
            journalForm = journal_formset(request.POST, queryset=KegiatanJurnal.objects.filter(is_active = True).order_by('date'), prefix='journal')

            if journalForm.is_valid():
                for journal in journalForm:
                    journal_item = journalForm.save()
                
                messages.add_message(request,messages.INFO,'Jurnal berhasil diupdate.')
                return redirect('/kegiatan/jurnal/')
            else:
                messages.add_message(request,messages.ERROR,'Jurnal gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'journalForm':journalForm,
                'table_head':table_head,
                'last_total':last_total,
                }
    
                return render(request,'backend/kegiatan/week_journal_update.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Journal gagal diupdate.')
            journalForm = KegiatanAkuntasiForm(data = request.POST, instance=gl)

            context = {
                'title':title,
                'menu':menu,
                'journalForm':journalForm,
                'table_head':table_head,
                'last_total':last_total,
            }
    
            return render(request,'backend/kegiatan/week_journal_update.html',context)
    else:
        journalForm = journal_formset(queryset=KegiatanJurnal.objects.filter(is_active = True).order_by('date'), prefix='journal')

        context = {
            'title':title,
            'menu':menu,
            'journalForm':journalForm,
            'table_head':table_head,
            'last_total':last_total,
            }

        return render(request,'backend/kegiatan/week_journal_update.html',context)

def show_kegiatan_transaksi(request):
    menu = ['Beranda','Kegiatan Buku Besar']
    title = 'Kegiatan Buku Besar'

    # first_date = last_friday = saldo_sebelumnya = pemasukan = pengeluaran = saldo = 2

    rekening_list = RekeningMasjid.objects.all().order_by('id')
    rekening = RekeningMasjid.objects.filter(is_primary = True).first()
    rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()

    selected_date = KegiatanJurnal.objects.order_by('id').last()
    if selected_date:
        first_date = selected_date.date.astimezone(current_tzinfo)
        last_date = first_date + timedelta(days=7)

        gl = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte = last_date).order_by('date')

        kegiatan_journal = KegiatanJurnal.objects.filter(date__date__lte = last_date)
        # kegiatan_akuntasi = KegiatanAkuntasi.objects.filter(date__date__lte = last_date)
        coa_credit = ChartOfAccounts.objects.get(account_name = 'Beban Operasional')
        coa_debet = ChartOfAccounts.objects.get(account_name = 'Pendapatan')

        if kegiatan_journal.last():
            # saldo_sebelumnya = kegiatan_journal.filter(date__date = first_date, coa = coa_debet,transaction='Saldo Akhir').last().balance
            pemasukan =kegiatan_journal.filter(coa = coa_debet, transaction='Jumlah Pemasukan Infaq/Sadaqah').last().balance
            pengeluaran = kegiatan_journal.filter(coa = coa_credit).last().balance
            saldo = kegiatan_journal.filter(coa = coa_debet,transaction='Saldo Akhir').last().balance
            # pemasukan =kegiatan_journal.filter(coa = coa_debet, transaction='Jumlah Pemasukan Infaq/Sadaqah').last().balance
            # pengeluaran = kegiatan_journal.filter(coa = coa_credit).last().balance
            # saldo = kegiatan_journal.filter(coa = coa_debet,transaction='Saldo Akhir').last().balance
    else:
        first_date = datetime.now().astimezone(current_tzinfo).date()
        last_date = first_date + timedelta(days=7)
        gl = KegiatanAkuntasi.objects.all().order_by('date')
        
        pemasukan = 0
        pengeluaran = 0
        saldo = 0
    

    context = {
        'title':title,
        'menu':menu,
        'first_date':first_date,
        'last_date':last_date,
        # 'saldo_sebelumnya':saldo_sebelumnya,
        'pemasukan':pemasukan,
        'pengeluaran':pengeluaran,
        'saldo':saldo,
        'gl':gl,
        'rekening_list':rekening_list,
        'rekening':rekening,
        'rekening_attachment':rekening_attachment,
        }

    return render(request, 'frontend/kegiatan/kegiatan_akuntasi_show.html',context)

def show_week_journal(request):
    pass