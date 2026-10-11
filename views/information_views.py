from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render, redirect
from django.http import HttpRequest
import requests
import json

#Set Logg
import logging
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
# from finance.models import *
# from finance.forms import *
# from team.models import *
# from information.models import *
# from information.forms import *
from portfolio.models import *
from banner.models import *
from gallery.models import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

from django.utils import timezone
current_tzinfo = timezone.get_current_timezone()

import random

#REKENING
def show_rekening(request):
    menu = ['Beranda','Rekening Masjid']
    title = 'Rekening Masjid'

    rekening_list = RekeningMasjid.objects.all().order_by('id')
    rekening = RekeningMasjid.objects.filter(is_primary = True).first()
    rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()

    context = {
        'title':title,
        'menu':menu,
        'rekening_list':rekening_list,
        'rekening':rekening,
        'rekening_attachment':rekening_attachment,
        }

    return render(request, 'frontend/information/rekening_masjid_show.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def rekening_list(request):
    menu = ['Home','Daftar Rekening Masjid']
    title = 'Daftar Rekening Masjid'

    rekening_list = RekeningMasjid.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'rekening_list':rekening_list}

    return render(request, 'backend/information/rekening_masjid_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def rekening_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Rekening']
    title = 'Tambah Rekening'

    if request.method == 'POST':
        try:
            rekeningForm = RekeningMasjidForm(data = request.POST)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(data = request.POST, files=request.FILES)

            if rekeningForm.is_valid() and rekeningAttachmentForm.is_valid():
                rekening = rekeningForm.save()

                attachment = rekeningAttachmentForm.save(commit=False)
                attachment.rekening = rekening
                attachment.save()
                
                messages.add_message(request,messages.INFO,rekening.no_rek+' successfully added.')

                return redirect('/rekening/list/')
            else:
                raise forms.ValidationError("Data rekening tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Data rekening tidak berhasil ditambahkan.')
            rekeningForm = RekeningMasjidForm(data = request.POST)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'rekeningForm':rekeningForm,
                'rekeningAttachmentForm':rekeningAttachmentForm,
            }
    
            return render(request,'backend/information/rekening_masjid_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Data rekening tidak berhasil ditambahkan.')
            rekeningForm = RekeningMasjidForm(data = request.POST)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'rekeningForm':rekeningForm,
                'rekeningAttachmentForm':rekeningAttachmentForm,
            }
    
            return render(request,'backend/information/rekening_masjid_form.html',context)
    else:
        rekeningForm = RekeningMasjidForm()
        rekeningAttachmentForm = RekeningMasjidAttachmentForm()

        context = {
            'title':title,
            'rekeningForm':rekeningForm,
            'rekeningAttachmentForm':rekeningAttachmentForm,
            }

        return render(request,'backend/information/rekening_masjid_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def rekening_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Transaksi']
    title = 'Ubah Transaksi'

    id = decoding_id(id)
    
    rekening = RekeningMasjid.objects.filter(id=id).first()
    rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()

    if request.method == 'POST':
        try:
            rekeningForm = RekeningMasjidForm(data = request.POST, instance=rekening)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(data = request.POST, files=request.FILES, instance = rekening_attachment)

            if rekeningForm.is_valid():
                rekening = rekeningForm.save()

                rekening_attachment = rekeningAttachmentForm.save(commit=False)
                rekening_attachment.general_ledger = rekening
                rekening_attachment.save()
                
                messages.add_message(request,messages.INFO,rekening.no_rek+' berhasil diedit.')
                return redirect('/rekening/list/')
            else:
                messages.add_message(request,messages.ERROR,rekening.no_rek+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'rekeningForm':rekeningForm,
                'rekeningAttachmentForm':rekeningAttachmentForm,
                }
    
                return render(request,'backend/information/rekening_masjid_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,rekening.no_rek+' gagal diupdate.')
            rekeningForm = RekeningMasjidForm(data = request.POST, instance=rekening)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(data = request.POST, files=request.FILES, instance = rekening_attachment)

            context = {
                'title':title,
                'menu':menu,
                'rekeningForm':rekeningForm,
                'rekeningAttachmentForm':rekeningAttachmentForm,
            }
    
            return render(request,'backend/information/rekening_masjid_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            rekeningForm = RekeningMasjidForm(instance=rekening)
            rekeningAttachmentForm = RekeningMasjidAttachmentForm(instance = rekening_attachment)

            context = {
                'title':title,
                'menu':menu,
                'rekeningForm':rekeningForm,
                'rekeningAttachmentForm':rekeningAttachmentForm,
                }

            return render(request,'backend/information/rekening_masjid_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,rekening.no_rek+' berhasil dihapus.')

            rekening.delete()
            if rekening_attachment:
                rekening_attachment.delete()
            return redirect('/rekening/list/')

#KutipanPilihan
def show_kutipan(request):
    menu = ['Beranda','Kutipan Pilihan']
    title = 'Kutipan Pilihan'

    kutipan_list = KutipanPilihan.objects.all().order_by('id')

    context = {
        'title':title,
        'menu':menu,
        'kutipan_list':kutipan_list}

    return render(request, 'frontend/information/kutipan_show.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kutipan_list(request):
    menu = ['Home','Kutipan List']
    title = 'Kutipan List'

    kutipan_list = KutipanPilihan.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'kutipan_list':kutipan_list}

    return render(request, 'backend/information/kutipan_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kutipan_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Kutipan']
    title = 'Tambah Kutipan'

    if request.method == 'POST':
        try:
            kutipanForm = KutipanPilihanForm(data = request.POST)

            if kutipanForm.is_valid():
                kutipan = kutipanForm.save()
                
                messages.add_message(request,messages.INFO,kutipan.title+' successfully added.')

                return redirect('/kutipan/list/')
            else:
                raise forms.ValidationError("Data kutipan tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Data kutipan tidak berhasil ditambahkan.')
            kutipanForm = KutipanPilihanForm(data = request.POST)

            context = {
                'title':title,
                'kutipanForm':kutipanForm,
            }
    
            return render(request,'backend/information/kutipan_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Data kutipan tidak berhasil ditambahkan.')
            context = {
                'title':title,
                'kutipanForm':kutipanForm,
            }
    
            return render(request,'backend/information/kutipan_form.html',context)
    else:
        kutipanForm = KutipanPilihanForm()

        context = {
            'title':title,
            'kutipanForm':kutipanForm,
            }

        return render(request,'backend/information/kutipan_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kutipan_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Transaksi']
    title = 'Ubah Transaksi'

    id = decoding_id(id)
    
    kutipan = KutipanPilihan.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            kutipanForm = KutipanPilihanForm(data = request.POST, instance=kutipan)

            if kutipanForm.is_valid():
                kutipan = kutipanForm.save()
                
                messages.add_message(request,messages.INFO,kutipan.title+' berhasil diedit.')
                return redirect('/kutipan/list/')
            else:
                messages.add_message(request,messages.ERROR,kutipan.title+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'kutipanForm':kutipanForm,
                }
    
                return render(request,'backend/information/kutipan_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,kutipan.title+' gagal diupdate.')
            kutipanForm = KutipanPilihanForm(data = request.POST, instance=kutipan)

            context = {
                'title':title,
                'menu':menu,
                'kutipanForm':kutipanForm,
            }
    
            return render(request,'backend/information/kutipan_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            kutipanForm = KutipanPilihanForm(instance=kutipan)

            context = {
                'title':title,
                'menu':menu,
                'kutipanForm':kutipanForm,
                }

            return render(request,'backend/information/kutipan_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,kutipan.title+' berhasil dihapus.')

            kutipan.delete()
            
            return redirect('/kutipan/list/')

#KhutbahJumat
def show_khutbah(request):
    menu = ['Beranda','Khutbah Jumat']
    title = 'Khutbah Jumat'
    quotes = 'Khutbah Jumat'

    khutbah_list = KhutbahJumat.objects.all().order_by('id')

    context = {
        'title':title,
        'menu':menu,
        'quotes':quotes,
        'khutbah_list':khutbah_list}

    return render(request, 'frontend/information/khutbah_jumat_show.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def khutbah_list(request):
    menu = ['Home','Daftar Khutbah']
    title = 'Daftar Khutbah'

    khutbah_list = KhutbahJumat.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'khutbah_list':khutbah_list}

    return render(request, 'backend/information/khutbah_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def khutbah_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Khutbah']
    title = 'Tambah Khutbah'

    if request.method == 'POST':
        try:
            khutbahForm = KhutbahJumatForm(data = request.POST)
            khutbahAttachmentForm = KhutbahJumatAttachmentForm(data = request.POST, files=request.FILES)

            if khutbahForm.is_valid():
                khutbah = khutbahForm.save()

                if khutbahAttachmentForm.is_valid():
                    attachment = khutbahAttachmentForm.save(commit=False)
                    attachment.khutbah = khutbah
                    attachment.save()
                
                messages.add_message(request,messages.INFO,khutbah.title+' successfully added.')

                return redirect('/khutbah/list/')
            else:
                raise forms.ValidationError("Data khutbah tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Data khutbah tidak berhasil ditambahkan.')
            khutbahForm = KhutbahJumatForm(data = request.POST)
            khutbahAttachmentForm = KhutbahJumatAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'khutbahForm':khutbahForm,
                'khutbahAttachmentForm':khutbahAttachmentForm,
            }
    
            return render(request,'backend/information/khutbah_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Data khutbah tidak berhasil ditambahkan.')
            khutbahForm = KhutbahJumatForm(data = request.POST)
            khutbahAttachmentForm = KhutbahJumatAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'khutbahForm':khutbahForm,
                'khutbahJumatAttachmentForm':khutbahAttachmentForm,
            }
    
            return render(request,'backend/information/khutbah_form.html',context)
    else:
        khutbahForm = KhutbahJumatForm()
        khutbahAttachmentForm = KhutbahJumatAttachmentForm()

        context = {
            'title':title,
            'khutbahForm':khutbahForm,
            'khutbahAttachmentForm':khutbahAttachmentForm,
            }

        return render(request,'backend/information/khutbah_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def khutbah_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Khutbah']
    title = 'Ubah Khutbah'

    id = decoding_id(id)
    
    khutbah = KhutbahJumat.objects.filter(id=id).first()
    # khutbah_attachment = KhutbahJumatAttachment.objects.filter(khutbah = khutbah).first()

    if request.method == 'POST':
        try:
            khutbahForm = KhutbahJumatForm(data = request.POST, instance=khutbah)
            # khutbahAttachmentForm = KhutbahJumatAttachmentForm(data = request.POST, files=request.FILES, instance = khutbah_attachment)

            if khutbahForm.is_valid():
                khutbah = khutbahForm.save()

                # khutbah_attachment = khutbahAttachmentForm.save(commit=False)
                # khutbah_attachment.khutbah = khutbah
                # khutbah_attachment.save()
                
                messages.add_message(request,messages.INFO,khutbah.title+' berhasil diedit.')
                return redirect('/khutbah/list/')
            else:
                messages.add_message(request,messages.ERROR,khutbah.title+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'khutbahForm':khutbahForm,
                # 'khutbahAttachmentForm':khutbahAttachmentForm,
                }
    
                return render(request,'backend/information/rekening_masjid_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,khutbah.no_rek+' gagal diupdate.')
            khutbahForm = KhutbahJumatForm(data = request.POST, instance=khutbah)
            # khutbahAttachmentForm = KhutbahJumatAttachmentForm(data = request.POST, files=request.FILES, instance = khutbah_attachment)

            context = {
                'title':title,
                'menu':menu,
                'khutbahForm':khutbahForm,
                # 'khutbahAttachmentForm':khutbahAttachmentForm,
            }
    
            return render(request,'backend/information/khutbah_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            khutbahForm = KhutbahJumatForm(instance=khutbah)
            # khutbahAttachmentForm = KhutbahJumatAttachmentForm(instance = khutbah_attachment)

            context = {
                'title':title,
                'menu':menu,
                'khutbahForm':khutbahForm,
                # 'khutbahAttachmentForm':khutbahAttachmentForm,
                }

            return render(request,'backend/information/khutbah_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,khutbah.title+' berhasil dihapus.')

            khutbah.delete()
            # if khutbah_attachment:
            #     khutbah_attachment.delete()
            return redirect('/khutbah/list/')

#KegiatanMasjid
def show_kegiatan(request):
    menu = ['Beranda','Kegiatan Masjid']
    title = 'Kegiatan Masjid'

    kegiatan_list = KegiatanMasjid.objects.all().order_by('id')


    client = Client.objects.all()

    page = request.GET.get('page',1)

    paginator = Paginator(kegiatan_list, per_page=10)

    try:
        kegiatans = paginator.page(page)
    except PageNotAnInteger:
        kegiatans = paginator.page(1)
    except EmptyPage:
        kegiatans = paginator.page(paginator.num_pages)

    context = {
        'title':title,
        'menu':menu,
        'kegiatans':kegiatans,
        'client':client,
        }

    return render(request, 'frontend/information/kegiatan_masjid_show.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_list(request):
    menu = ['Home','kegiatan List']
    title = 'kegiatan List'

    kegiatan_list = KegiatanMasjid.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'kegiatan_list':kegiatan_list}

    return render(request, 'backend/information/kegiatan_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Kegiatan']
    title = 'Tambah Kegiatan'

    if request.method == 'POST':
        try:
            kegiatanForm = KegiatanMasjidForm(data = request.POST)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(data = request.POST, files=request.FILES)

            if kegiatanForm.is_valid() and kegiatanAttachmentForm.is_valid():
                kegiatan = kegiatanForm.save()

                attachment = kegiatanAttachmentForm.save(commit=False)
                attachment.kegiatan = kegiatan
                attachment.save()
                
                messages.add_message(request,messages.INFO,kegiatan.title+' successfully added.')

                return redirect('/kegiatan/list/')
            else:
                raise forms.ValidationError("Data kegiatan tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Data kegiatan tidak berhasil ditambahkan.')
            kegiatanForm = KegiatanMasjidForm(data = request.POST)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'kegiatanForm':kegiatanForm,
                'kegiatanAttachmentForm':kegiatanAttachmentForm,
            }
    
            return render(request,'backend/information/kegiatan_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Data kegiatan tidak berhasil ditambahkan.')
            kegiatanForm = KegiatanMasjidForm(data = request.POST)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'kegiatanForm':kegiatanForm,
                'kegiatanAttachmentForm':kegiatanAttachmentForm,
            }
    
            return render(request,'backend/information/kegiatan_form.html',context)
    else:
        kegiatanForm = KegiatanMasjidForm()
        kegiatanAttachmentForm = KegiatanMasjidAttachmentForm()

        context = {
            'title':title,
            'kegiatanForm':kegiatanForm,
            'kegiatanAttachmentForm':kegiatanAttachmentForm,
            }

        return render(request,'backend/information/kegiatan_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def kegiatan_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Kegiatan']
    title = 'Ubah Kegiatan'

    id = decoding_id(id)
    
    kegiatan = KegiatanMasjid.objects.filter(id=id).first()
    kegiatan_attachment = KegiatanMasjidAttachment.objects.filter(kegiatan = kegiatan).first()

    if request.method == 'POST':
        try:
            kegiatanForm = KegiatanMasjidForm(data = request.POST, instance=kegiatan)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(data = request.POST, files=request.FILES, instance = kegiatan_attachment)

            if kegiatanForm.is_valid():
                kegiatan = kegiatanForm.save()

                kegiatan_attachment = kegiatanAttachmentForm.save(commit=False)
                kegiatan_attachment.kegiatan = kegiatan
                kegiatan_attachment.save()
                
                messages.add_message(request,messages.INFO,kegiatan.title+' berhasil diedit.')
                return redirect('/kegiatan/list/')
            else:
                messages.add_message(request,messages.ERROR,kegiatan.title+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'kegiatanForm':kegiatanForm,
                'kegiatanAttachmentForm':kegiatanAttachmentForm,
                }
    
                return render(request,'backend/information/kegiatan_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,kegiatan.title+' gagal diupdate.')
            kegiatanForm = KegiatanMasjidForm(data = request.POST, instance=kegiatan)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(data = request.POST, files=request.FILES, instance = kegiatan_attachment)

            context = {
                'title':title,
                'menu':menu,
                'kegiatanForm':kegiatanForm,
                'kegiatanAttachmentForm':kegiatanAttachmentForm,
            }
    
            return render(request,'backend/information/kegiatan_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            kegiatanForm = KegiatanMasjidForm(instance=kegiatan)
            kegiatanAttachmentForm = KegiatanMasjidAttachmentForm(instance = kegiatan_attachment)

            context = {
                'title':title,
                'menu':menu,
                'kegiatanForm':kegiatanForm,
                'kegiatanAttachmentForm':kegiatanAttachmentForm,
                }

            return render(request,'backend/information/kegiatan_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,kegiatan.title+' berhasil dihapus.')

            kegiatan.delete()
            if kegiatan_attachment:
                kegiatan_attachment.delete()
            return redirect('/kegiatan/list/')

#Show Wallpaper
def show_wallpaper(request):
    menu = ['Beranda','Masjid Ar-Raudah']
    title = 'Masjid Ar-Raudah'

    banner = Banner.objects.filter(category = 2).order_by('id')
    naration = TeamNaration.objects.all()

    # ✅ ambil banner iqamah yang aktif
    banner_iqamah = BannerIqamah.objects.filter(is_active=True).first()
    context = {
        'title': title,
        'menu': menu,
        'banner': banner,
        'naration': naration,
        'banner_iqamah': banner_iqamah   
    }

    return render(request, 'frontend/information/wallpaper.html', context)

def show_slider_jumat(request):
    menu = ['Beranda','Masjid Ar-Raudah']
    title = 'Masjid Ar-Raudah'

    banner = Banner.objects.filter(category = 3).order_by('id')
    naration = TeamNaration.objects.all()

    context = {
        'title':title,
        'menu':menu,
        'banner':banner,
        'naration':naration
        }

    return render(request, 'frontend/information/full_picture_wallpaper.html',context)

def show_wallpaper2(request):
    menu = ['Beranda','Masjid Ar-Raudah']
    title = 'Masjid Ar-Raudah'

    banner = Banner.objects.all().order_by('id')
    naration = TeamNaration.objects.all()

    context = {
        'title':title,
        'menu':menu,
        'banner':banner,
        'naration':naration
        }

    return render(request, 'frontend/information/wallpaper2.html',context)

def show_wallpaper3(request):
    menu = ['Beranda','Masjid Ar-Raudah']
    title = 'Masjid Ar-Raudah'

    banner = KegiatanMasjidAttachment.objects.filter(is_active = True).order_by('id')
    naration = TeamNaration.objects.all()

    context = {
        'title':title,
        'menu':menu,
        'banner':banner,
        'naration':naration
        }
    
    return render(request, 'frontend/information/wallpaper3.html',context)  

# def wallpaper_view(request):

    

#     return render(request, "wallpaper.html", {"playlist": playlist})

def show_standby_wallpaper(request):
    menu = ['Beranda','Masjid Ar-Raudah']
    title = 'Masjid Ar-Raudah'

    galeri = Gallery.objects.all().order_by('id')
    naration = TeamNaration.objects.all()

    context = {
        'title':title,
        'menu':menu,
        'galeri':galeri,
        'naration':naration
        }

    return render(request, 'frontend/information/standby_wallpaper.html',context)
    
