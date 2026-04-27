from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.shortcuts import render, redirect
from django.http import HttpRequest

from django.utils import timezone
from datetime import timedelta

#Set Logg
import logging
from qurban.forms import *
from qurban.models import *

from django.contrib.sites.shortcuts import get_current_site
from qrcode import make

import re
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
from finance.models import *
from finance.forms import *
from team.models import *
from information.models import *
from information.forms import *
from app.crons import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

current_tzinfo = timezone.get_current_timezone()

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_list(request):
    menu = ['Home','COA Group List']
    title = 'COA Group List'

    coa_group = ChartOfAccountGroup.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'coa_group':coa_group}

    return render(request, 'backend/finance/coa_group_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Add New COA Group']
    title = 'Add New COA Group'

    if request.method == 'POST':
        try:
            coaGroupForm = COAGroupForm(data = request.POST)
            if coaGroupForm.is_valid():
                coa = coaGroupForm.save()
                
                messages.add_message(request,messages.INFO,coa.group_name +' successfully added.')

                return redirect('/coa/group/')
            else:
                raise forms.ValidationError("COA Group tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'COA Group tidak berhasil ditambahkan.')
            coaGroupForm = COAGroupForm(data = request.POST)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/finance/coa_group_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA Group tidak berhasil ditambahkan.')
            coaGroupForm = COAGroupForm(data = request.POST)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/finance/coa_group_form.html',context)
    else:
        coaGroupForm = COAGroupForm()

        context = {
            'title':title,
            'coaGroupForm':coaGroupForm,
            }

        return render(request,'backend/finance/coa_group_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit COA Group']
    title = 'Edit New COA Group'

    id = decoding_id(id)
    
    coa_group = ChartOfAccountGroup.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            coaGroupForm = COAGroupForm(data = request.POST, instance=coa_group)

            if coaGroupForm.is_valid():
                coa_group = coaGroupForm.save()
                
                messages.add_message(request,messages.INFO,coa_group.group_name +' berhasil diedit.')
                return redirect('/coa/group/')
            else:
                messages.add_message(request,messages.ERROR,coa_group.group_name+' gagal diupdate.')

                context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
                }
    
                return render(request,'backend/finance/coa_group_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,coa_group.group_name +' gagal diupdate.')
            coaGroupForm = COAGroupForm(instance=coa_group)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
            }
    
            return render(request,'backend/finance/coa_group_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            coaGroupForm = COAGroupForm(instance=coa_group)

            context = {
                'title':title,
                'coaGroupForm':coaGroupForm,
                }

            return render(request,'backend/finance/coa_group_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,coa_group.group_name+' berhasil dihapus.')
            coa_group.delete()
            return redirect('/coa/group/')

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_list(request):
    menu = ['Home','COA List']
    title = 'COA List'

    coa = ChartOfAccount.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'coa':coa}

    return render(request, 'backend/finance/coa_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah COA Baru']
    title = 'Tambah COA Baru'

    if request.method == 'POST':
        try:
            coaForm = COAForm(data = request.POST)
            if coaForm.is_valid():
                coa = coaForm.save()
                
                messages.add_message(request,messages.INFO,coa.account_name +' successfully added.')

                return redirect('/coa/')
            else:
                raise forms.ValidationError("COA tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            coaForm = COAForm(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/finance/coa_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            coaForm = COAForm(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/finance/coa_form.html',context)
    else:
        coaForm = COAForm()

        context = {
            'title':title,
            'menu':menu,
            'coaForm':coaForm,
            }

        return render(request,'backend/finance/coa_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Edit COA']
    title = 'Edit New COA'

    id = decoding_id(id)
    
    coa = ChartOfAccount.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            coaForm = COAForm(data = request.POST, instance=coa)

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
    
                return render(request,'backend/finance/coa_form.html',context)

        except ValidationError as e:
            messages.add_message(request,messages.ERROR,coa.account_name+' gagal diupdate.')
            coaForm = COAForm(instance=coa)

            context = {
                'title':title,
                'coaForm':coaForm,
            }
    
            return render(request,'backend/finance/coa_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            coaForm = COAForm(instance=coa)

            context = {
                'title':title,
                'menu':menu,
                'coaForm':coaForm,
                }

            return render(request,'backend/finance/coa_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,coa.account_name +' berhasil dihapus.')
            coa.delete()
            return redirect('/coa/')

@login_required(login_url='/admin/who-login/')
@admin_only
def general_ledger_list(request):
    menu = ['Home','General Ledger']
    title = 'General Ledger'

    gl = GeneralLedger.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'gl':gl}

    return render(request, 'backend/finance/general_ledger_list.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def general_ledger_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Transaksi Baru']
    title = 'Transaksi Baru'

    if request.method == 'POST':
        try:
            glForm = GeneralLedgerForm(data = request.POST)
            glAttachmentForm = GeneralLedgerAttachmentForm(data = request.POST, files=request.FILES)

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
            glForm = GeneralLedgerForm(data = request.POST)
            glAttachmentForm = GeneralLedgerAttachmentForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
            }
    
            return render(request,'backend/finance/general_ledger_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'COA tidak berhasil ditambahkan.')
            glForm = GeneralLedgerForm(data = request.POST, files=request.FILES)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
            }
    
            return render(request,'backend/finance/general_ledger_form.html',context)
    else:
        glForm = GeneralLedgerForm()
        glAttachmentForm = GeneralLedgerAttachmentForm()

        context = {
            'title':title,
            'menu':menu,
            'glForm':glForm,
            'glAttachmentForm':glAttachmentForm,
            }

        return render(request,'backend/finance/general_ledger_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def general_ledger_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Transaksi']
    title = 'Ubah Transaksi'

    id = decoding_id(id)
    
    gl = GeneralLedger.objects.filter(id=id).first()
    gl_attachment = GeneralLedgerAttachment.objects.filter(general_ledger = gl).first()

    if request.method == 'POST':
        try:
            glForm = GeneralLedgerForm(data = request.POST, instance=gl)
            glAttachmentForm = GeneralLedgerAttachmentForm(data = request.POST, files=request.FILES, instance = gl_attachment)

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
    
                return render(request,'backend/finance/general_ledger_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,gl.transaction+' gagal diupdate.')
            glForm = GeneralLedgerForm(data = request.POST, instance=gl)
            glAttachmentForm = GeneralLedgerAttachmentForm(data = request.POST, files=request.FILES, instance = gl_attachment)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
            }
    
            return render(request,'backend/finance/general_ledger_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            glForm = GeneralLedgerForm(instance=gl)
            glAttachmentForm = GeneralLedgerAttachmentForm(instance = gl_attachment)

            context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'glAttachmentForm':glAttachmentForm,
                }

            return render(request,'backend/finance/general_ledger_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,gl.transaction+' berhasil dihapus.')
            gl.delete()
            return redirect('/gl/')

@login_required(login_url='/admin/who-login/')
@admin_only
def transaction_book_list(request):
    menu = ['Home','Buku Besar']
    title = 'Buku Besar'

    gl = GeneralLedger.objects.all().order_by('order_no')
    context = {
        'title':title,
        'menu':menu,
        'gl':gl,
        }

    return render(request, 'backend/finance/transaction_table.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
@transaction.atomic
def transaction_book_update(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah/Ubah Transaksi']
    title = 'Tambah/Ubah Transaksi'
    
    transaction_count = 0
    week_start_point = WeekJournal.objects.filter(status='Saldo Akhir', is_active = True).last()
    start_week = week_start_point.date - timedelta(weeks=2)
    last_saldo = WeekJournal.objects.filter(status='Saldo Akhir', is_active = True, date__gte = start_week).first()
   
    #mengambil dan mengubah format tanggal dari weekjournal menjadi integer
    #last_saldo_order_no = str(last_saldo.date)
    #last_saldo_date = datetime.strptime(last_saldo_order_no, "%Y-%m-%d %H:%M:%S%z").date()
    #start_date = last_saldo_date - timedelta(weeks=2)
    
    # gl_last_saldo = GeneralLedger.objects.filter(id = 286 ).last()
    gl_last_saldo = GeneralLedger.objects.filter(order_no = last_saldo.gl_order_no ).last()# 213
    
    saldo_count = GeneralLedger.objects.filter(last_checked = False).last()
    
    ls_count = saldo_count.balance

    # selected_wj = WeekJournal.objects.filter(gl_order_no__lt = n_count)
    # last_selected_wj = selected_wj.last()
    # selected_row = GeneralLedger.objects.filter(order_no = last_saldo.gl_order_no).last()
    # n_count = GeneralLedger.objects.filter(id__lte  = selected_row.id).count()

    n_count = last_saldo.gl_order_no
    gl_count = gl_last_saldo.order_no # 213
    
    # print(gl_count)

    if(last_saldo):
        last_total = last_saldo.balance
    else:
        last_total = 0
    gl_formset = modelformset_factory(GeneralLedger, form=GeneralLedgerForm, extra=transaction_count, min_num=1, max_num=300)
    

    table_head = mark_safe(
                        "<th width='5%'>No</th>"
					    "<th width='10%' data-priority='1'>Tanggal</th>"
						"<th width='10%'>Akun</th>"
						"<th width='25%' data-priority='2'>Transaksi</th>"
						"<th width='10%' data-priority='4'>Debet</th>"
						"<th width='10%' data-priority='5'>Kredit</th>"
						"<th width='10%' data-priority='3'>Saldo</th>"
						"<th width='10%'>Aksi</th>")

    if request.method == 'POST':
        try:
            glForm = gl_formset(request.POST, queryset=GeneralLedger.objects.filter(order_no__gte = n_count).order_by('id'), prefix='gl')

            if glForm.is_valid():
                #check date difungsikan untuk mengetahui iterasi
                check_date = None
                reorder = False
                for index, gl in enumerate(glForm):
                    index = gl_count + index 
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
                        if check_date > gl_item.date:
                            check_date = gl_item.date
                            reorder = True
                        elif not reorder:
                            check_date = gl_item.date

                if reorder:
                    #clear week journal
                    del_journal = WeekJournal.objects.filter(date__date__gte = check_date).delete()

                    #reorder and calculate
                    gl_last_order = GeneralLedger.objects.filter(date__date__lt = check_date).order_by('order_no','date').last()
                    if gl_last_order:
                        last_order = gl_last_order.order_no
                        last_balance = gl_last_order.balance
                    else:
                        last_order = 0
                        last_balance = 0

                    gl_list = GeneralLedger.objects.filter(date__date__gte = check_date).order_by('date','order_no')
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
                GeneralLedger.objects.update(last_checked=False)
                last_checked = GeneralLedger.objects.last()
                last_checked.last_checked = True
                last_checked.save()
                        
                update_week_journal()
                messages.add_message(request,messages.INFO,'GL berhasil diupdate.')
                return redirect('/transaction/book/')
            else:
                messages.add_message(request,messages.ERROR,'GL gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'glForm':glForm,
                'table_head':table_head,
                'last_total':last_total,
                'n_count':n_count,
                'ls_count':ls_count,
                }
    
                return render(request,'backend/finance/transaction_table_update.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'GL gagal diupdate.')
            glForm = GeneralLedgerForm(data = request.POST, instance=gl)

            context = {
                'title':title,  
                'menu':menu,
                'glForm':glForm,
                'table_head':table_head,
                'last_total':last_total,
                'n_count':n_count,
                'ls_count':ls_count,
            }
    
            return render(request,'backend/finance/transaction_table_update.html',context)
    else:
        glForm = gl_formset(queryset=GeneralLedger.objects.filter(order_no__gte = n_count).order_by('id'), prefix='gl')
        
        context = {
            'title':title,
            'menu':menu,
            'glForm':glForm,
            'table_head':table_head,
            'last_total':last_total,
            'n_count':n_count,
            'ls_count':ls_count,
            }

        return render(request,'backend/finance/transaction_table_update.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def week_journal_list(request):
    menu = ['Home','Jurnal Mingguan']
    title = 'Jurnal Mingguan'

    week_journal = WeekJournal.objects.filter(is_active = True).order_by('date')
    context = {
        'title':title,
        'menu':menu,
        'week_journal':week_journal,
        }

    return render(request, 'backend/finance/week_journal.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def week_journal_update(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Validasi jurnal']
    title = 'Validasi Jurnal'
    
    journal_count = 0
    last_saldo = WeekJournal.objects.filter(status='Saldo Akhir', is_active = True).last()
    if(last_saldo):
        last_total = last_saldo.balance
    else:
        last_total = 0

    journal_formset = modelformset_factory(WeekJournal,form=WeekJournalForm, extra=journal_count,min_num=1,max_num=300)

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
            journalForm = journal_formset(request.POST, queryset=WeekJournal.objects.filter(is_active = True).order_by('date'), prefix='journal')

            if journalForm.is_valid():
                for journal in journalForm:
                    journal_item = journalForm.save()
                
                messages.add_message(request,messages.INFO,'Jurnal berhasil diupdate.')
                return redirect('/journal/week/')
            else:
                messages.add_message(request,messages.ERROR,'Jurnal gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'journalForm':journalForm,
                'table_head':table_head,
                'last_total':last_total,
                }
    
                return render(request,'backend/finance/week_journal_update.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Journal gagal diupdate.')
            journalForm = GeneralLedgerForm(data = request.POST, instance=gl)

            context = {
                'title':title,
                'menu':menu,
                'journalForm':journalForm,
                'table_head':table_head,
                'last_total':last_total,
            }
    
            return render(request,'backend/finance/week_journal_update.html',context)
    else:
        journalForm = journal_formset(queryset=WeekJournal.objects.filter(is_active = True).order_by('date'), prefix='journal')

        context = {
            'title':title,
            'menu':menu,
            'journalForm':journalForm,
            'table_head':table_head,
            'last_total':last_total,
            }

        return render(request,'backend/finance/week_journal_update.html',context)

def show_general_ledger(request):
    menu = ['Beranda','Buku Besar']
    title = 'Buku Besar'

    rekening_list = RekeningMasjid.objects.all().order_by('id')
    rekening = RekeningMasjid.objects.filter(is_primary = True).first()
    rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()

    selected_friday = WeekJournal.objects.filter(is_active = True).order_by('id').last()
    if selected_friday:
        last_friday = selected_friday.date.astimezone(current_tzinfo)
        first_date = last_friday - timedelta(days=7)

        gl = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte = last_friday).order_by('date')

        week_journal = WeekJournal.objects.filter(date__date__lte = last_friday)
        coa_credit = ChartOfAccount.objects.get(account_name = 'Beban Operasional')
        coa_debet = ChartOfAccount.objects.get(account_name = 'Pendapatan')

        if week_journal.last():
            saldo_sebelumnya = week_journal.filter(date__date = first_date, coa = coa_debet,transaction='Saldo Akhir').last().balance
            pemasukan = week_journal.filter(coa = coa_debet, transaction='Jumlah Pemasukan Infaq/Sadaqah').last().balance
            pengeluaran = week_journal.filter(coa = coa_credit).last().balance
            saldo = week_journal.filter(coa = coa_debet,transaction='Saldo Akhir').last().balance
    else:
        gl = GeneralLedger.objects.all().order_by('date')
    

    context = {
        'title':title,
        'menu':menu,
        'first_date':first_date,
        'last_date':last_friday,
        'saldo_sebelumnya':saldo_sebelumnya,
        'pemasukan':pemasukan,
        'pengeluaran':pengeluaran,
        'saldo':saldo,
        'gl':gl,
        'rekening_list':rekening_list,
        'rekening':rekening,
        'rekening_attachment':rekening_attachment,
        }

    return render(request, 'frontend/finance/general_ledger_show.html',context)

def show_week_journal(request):
    pass

@login_required(login_url='/admin/who-login/')
@admin_only
def qurban_type_list(request):
    menu = ['Home','Tipe Qurban']
    title = 'Tipe Qurban'

    qurban_types = QurbanType.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'qurban_types':qurban_types,
        }

    return render(request, 'backend/qurban/qurban_type_list.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def qurban_type_add(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah Tipe Qurban']
    title = 'Tambah Tipe Qurban'

    if request.method == 'POST':
        try:
            typeForm = QurbanTypeForm(data = request.POST)

            if typeForm.is_valid():
                qurbanType = typeForm.save()
                
                messages.add_message(request,messages.INFO,qurbanType.qurban_type +' successfully added.')

                return redirect('/qurban/type/')
            else:
                raise forms.ValidationError("Transaksi tidak valid.")
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'Tipe Qurban tidak berhasil ditambahkan.')
            logger.error('Error ketika menambahkan Tipe Kurban: %s', e)
            typeForm = QurbanTypeForm(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'typeForm':typeForm,
            }
    
            return render(request,'backend/qurban/qurban_type_form.html',context)
        except Exception as e:
            messages.add_message(request,messages.ERROR,'Tipe Qurban tidak berhasil ditambahkan.')
            logger.error('Error ketika menambahkan Tipe Kurban: %s', e)
            typeForm = QurbanTypeForm(data = request.POST)

            context = {
                'title':title,
                'menu':menu,
                'typeForm':typeForm,
            }
    
            return render(request,'backend/qurban/qurban_type_form.html',context)
    else:
        typeForm = QurbanTypeForm()

        context = {
            'title':title,
            'menu':menu,
            'typeForm':typeForm,
            }

        return render(request,'backend/qurban/qurban_type_form.html',context)

@login_required(login_url='/admin/who-login/')
@admin_only
def qurban_type_update(request, status, id):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Ubah Tipe Qurban']
    title = 'Ubah Tipe Qurban'

    id = decoding_id(id)
    
    qurbanType = QurbanType.objects.filter(id=id).first()

    if request.method == 'POST':
        try:
            typeForm = QurbanTypeForm(data = request.POST, instance=qurbanType)

            if typeForm.is_valid():
                qurbanType = typeForm.save()
                
                messages.add_message(request,messages.INFO,qurbanType.qurban_type+' berhasil diedit.')
                return redirect('/qurban/type/')
            else:
                messages.add_message(request,messages.ERROR,qurbanType.qurban_type+' gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'typeForm':typeForm,
                }
    
                return render(request,'backend/qurban/qurban_type_form.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,typeForm.qurban_type+' gagal diupdate.')
            typeForm = QurbanTypeForm(data = request.POST, instance=qurbanType)

            context = {
                'title':title,
                'menu':menu,
                'typeForm':typeForm,
                }
    
            return render(request,'backend/qurban/qurban_type_form.html',context)
    elif request.method == 'GET':
        if status == 'edit':
            typeForm = QurbanTypeForm(instance=qurbanType)

            context = {
                'title':title,
                'menu':menu,
                'typeForm':typeForm,
                }

            return render(request,'backend/qurban/qurban_type_form.html',context)
        elif status == 'delete':
            messages.add_message(request,messages.WARNING,qurbanType.qurban_type+' berhasil dihapus.')
            qurbanType.delete()
            return redirect('/qurban/type/')
        
@login_required(login_url='/admin/who-login/')
@admin_only
def qurban_list(request):
    menu = ['Home','Daftar Qurban']
    title = 'Daftar Qurban'

    qurban_list = Qurban.objects.all().order_by('id')
    context = {
        'title':title,
        'menu':menu,
        'qurban_list':qurban_list,
        }

    return render(request, 'backend/qurban/qurban_list.html', context)

@login_required(login_url='/admin/who-login/')
@admin_only
def qurban_update(request):
    assert isinstance(request, HttpRequest)
    menu = ['Home','Tambah/Ubah Daftar Qurban']
    title = 'Tambah/Ubah Daftar Qurban'
    
    extra_list = 0
    qurban_list_formset = modelformset_factory(ShohibulQurban, form=QurbanForm, extra=extra_list, min_num=1, max_num=300)
    # n_count = ShohibulQurban.objects.count()
    
    table_head = mark_safe(
                        "<th width='5%'>No</th>"
					    "<th width='10%' data-priority='1'>Tanggal</th>"
						"<th width='10%'>Shohibul Qurban</th>"
						"<th width='10%' data-priority='2'>Father</th>"
						"<th width='10%' data-priority='4'>Gender</th>"
                        "<th width='20%' data-priority='5'>Informasi</th>"
                        "<th width='10%' data-priority='6'>Tipe Qurban</th>"
                        "<th width='15%' data-priority='6'>Group Qurban</th>"
						"<th width='10%'>Aksi</th>")

    if request.method == 'POST':
        try:
            qurbanListForm = qurban_list_formset(request.POST, queryset=ShohibulQurban.objects.all().order_by('id'), prefix='qurban')

            if qurbanListForm.is_valid():
                for index, qurbanForm in enumerate(qurbanListForm):
                    shohibul_qurban = qurbanForm.save()
                    
                    if shohibul_qurban:
                        #Create Barcode
                        current_site = get_current_site(request)
                        barcode_name = re.sub('[^a-zA-Z0-9 \n\.]', '',shohibul_qurban.name.replace(" ",""))
                        img = make(current_site.domain+'/certificate/'+barcode_name)
                        img_name = f'{str(barcode_name)}.png'
                        # img.save(settings.MEDIA_ROOT+'certificate'+img_name)
                        img.save(os.path.join(settings.MEDIA_ROOT,'certificate',img_name))

                        #Create Certificate URL
                        # shohibul_qurban.barcode.save(img_name, File(open(str(os.path.join(settings.MEDIA_ROOT,'certificate',img_name)),'rb')))
                        # shohibul_qurban.save()
                        
                        #Create Qurban
                        qurban_exists = Qurban.objects.filter(shohibul_qurban = shohibul_qurban).first()
                        if qurban_exists:
                            qurban_exists.qurban_date = qurbanForm.cleaned_data.get('qurban_date')
                            qurban_exists.qurban_type = qurbanForm.cleaned_data.get('qurban_type')
                            qurban_exists.qurban_group = qurbanForm.cleaned_data.get('qurban_group')
                        else:
                            qurban_exists = Qurban.objects.create(
                                shohibul_qurban = shohibul_qurban,
                                qurban_date = qurbanForm.cleaned_data.get('qurban_date'),
                                qurban_type = qurbanForm.cleaned_data.get('qurban_type'),
                                qurban_group = qurbanForm.cleaned_data.get('qurban_group')
                                )
                        
                        #Create Certificate URL
                        qurban_exists.barcode.save(img_name, File(open(str(settings.MEDIA_ROOT+'/certificate/'+img_name),'rb')))
                        qurban_exists.save()
                    
                messages.add_message(request,messages.INFO,'List Kurban berhasil diupdate.')
                return redirect('/qurban/')
                
            else:
                messages.add_message(request,messages.ERROR,'List Kurban gagal diupdate.')

                context = {
                'title':title,
                'menu':menu,
                'qurbanListForm':qurbanListForm,
                'table_head':table_head,
                }
    
                return render(request,'backend/qurban/qurban_update.html',context)
        except ValidationError as e:
            messages.add_message(request,messages.ERROR,'GL gagal diupdate.')
            qurbanForm = GeneralLedgerForm(data = request.POST, instance=qurban)

            context = {
                'title':title,  
                'menu':menu,
                'qurbanListForm':qurbanListForm,
                'table_head':table_head,
            }
    
            return render(request,'backend/qurban/qurban_update.html',context)
    else:
        qurbanListForm = qurban_list_formset(queryset=ShohibulQurban.objects.all().order_by('id'), prefix='qurban')
        
        context = {
            'title':title,
            'menu':menu,
            'qurbanListForm':qurbanListForm,
            'table_head':table_head,
            }

        return render(request,'backend/qurban/qurban_update.html',context)