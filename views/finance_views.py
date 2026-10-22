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
logger = logging.getLogger(__file__)

from app.decorators import *
from utils.utils import *
<<<<<<< HEAD
# from finance.models import *
# from finance.forms import *
# from team.models import *
# from information.models import *
# from information.forms import *
=======
from finance.models import *
from finance.forms import *
from team.models import *
from information.models import *
from information.forms import *
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609
from app.crons import *

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

current_tzinfo = timezone.get_current_timezone()

@login_required(login_url='/admin/who-login/')
@admin_only
def coa_group_list(request):
    menu = ['Home','Daftar COA Grup']
    title = 'Daftar COA Grup'

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
    menu = ['Home','Tambah COA Grup']
    title = 'Tambah COA Grup'

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
    menu = ['Home','Edit COA Grup']
    title = 'Edit COA Grup'

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
    menu = ['Home','Daftar COA']
    title = 'Daftar COA'

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
    title = 'Edit COA'

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