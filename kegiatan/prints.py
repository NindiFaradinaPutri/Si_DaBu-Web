from utils.utils import *
from app.decorators import *

import json


from django.http import JsonResponse, HttpResponse, HttpRequest
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

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

from kegiatan.models import *
from kegiatan.forms import *
from information.models import *

import requests

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

import calendar
from hijri_converter import Hijri, Gregorian
from django.utils import timezone
current_tzinfo = timezone.get_current_timezone()

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def print_kegiatan_zakat(request, start_date, end_date, pass_code):
    assert isinstance(request, HttpRequest)
    if pass_code == 'masjidnuok':
        start_date_format = datetime.strptime(start_date,'%d-%m-%Y').astimezone(current_tzinfo)
        end_date_format = datetime.strptime(end_date,'%d-%m-%Y').astimezone(current_tzinfo)
        year = int(str(end_date_format.year))
        month = int(str(end_date_format.month))
        month_indo = str(bulan_indo(month))
        date = int(str(end_date_format.day))

        hijri_date = Gregorian(year, month, date).to_hijri()
        hijri_date_day = hijri_date.day
        hijri_date_month = hijri_date.month_name()
        hijri_date_month_indo = bulan_hijriah_indo(hijri_date.month)
        hijri_date_year = hijri_date.year

        #bpn_code = "2308"
        #today = datetime.now().astimezone(current_tzinfo).date().strftime(('%Y/%m/%d'))
        #url_sholat = "https://api.myquran.com/v1/sholat/jadwal/"+bpn_code+'/'+today
        #headers = {"accept": "application/json"}
        #response = requests.get(url_sholat, headers=headers)
        #jadwal_sholat_raw = response.json()
        #jadwal_sholat_clean = jadwal_sholat_raw.get('data').get('jadwal')

        jadwal_sholat = {}
        #jadwal_sholat['dzuhur'] = str(jadwal_sholat_clean.get('dzuhur'))
        jadwal_sholat['dzuhur'] = '12:11'
        
        title = "LAPORAN KEGIATAN MASJID AR-RAUDAH IBADAH SHOLAT JUM'AT"
        #sub_title = 'TANGGAL '+ str(date) +' '+ str(month_indo).upper() +' '+ str(year) +' BERTEPATAN DENGAN '+str(hijri_date_day) +' '+ str(hijri_date_month_indo).upper() +' '+str(hijri_date_year)+' Hijriah'
        sub_title = 'TANGGAL '+ str(date) +' '+ str(month_indo).upper() +' '+ str(year) +' BERTEPATAN DENGAN '+str(hijri_date_day) +' '+ str(hijri_date_month_indo).upper() +' '+str(hijri_date_year)+' Hijriah'

        content_html = ''

        credit_saldo = 0
        debet_saldo = 0
    
        start_table = mark_safe(
                                '''<table class="table mb-0" id="datatable-rekening">
							    <thead>
								    <tr class="text-center">
									    <th>No</th>
									    <th>Transaksi</th>
                                        <th colspan='2'>Tanggal</th>
									    <th>Jumlah</th>
								    </tr>
							    </thead><tbody>''')

        content_table = ''

        if start_date_format:
            #minggu_sebelumnya = start_date_format - timedelta(days=7)
            #coa_last_point = ChartOfAccount.objects.get(account_name = 'Gaji dan Tunjangan')
            last_saldo = KegiatanJurnal.objects.filter(date__date = start_date_format, status='Saldo Akhir', is_active = True).last()
            
            #week_journal = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            week_journal = KegiatanAkuntasi.objects.filter(order_no = last_saldo.gl_order_no).order_by('date','id')

            if week_journal.last():
                exclude_transaction = week_journal.last()
                saldo_sebelumnya = week_journal.last().balance
            else:
                saldo_sebelumnya = 0

            if(saldo_sebelumnya):
                print_saldo = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
                debet_saldo += saldo_sebelumnya
            else:
                print_saldo = '-'

            next_order_no = KegiatanJurnal.objects.filter(gl_order_no__gt = exclude_transaction.order_no).first()

            content_table += mark_safe(
                                '''
                                <tr>
								    <td>%s</td>
								    <td>Saldo Minggu Sebelumnya</td>
								    <td class="text-center">%s</td>
								    <td class="text-center">Rp</td>
								    <td class="text-right">
									    %s
								    </td>
							    </tr>
                                '''%(1, 
                                     start_date_format.astimezone(current_tzinfo).strftime("%d %b %Y"), 
                                     print_saldo)
                                )

        if next_order_no:
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, order_no__lt = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')

        no_loop = 1
        if debet_gl :
            for index, list_item in enumerate(debet_gl):
                no_loop += 1
                if(list_item.debet):
                    saldo = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                    debet_saldo += list_item.debet
                else:
                    saldo = '-'
                    debet_saldo += 0

                content_table += mark_safe(
                                    '''
                                    <tr>
									    <td>%s</td>
									    <td>%s</td>
									    <td class="text-center">%s</td>
									    <td class="text-center">Rp</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(no_loop, list_item.transaction, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), saldo)
                                    )

            if(debet_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(debet_saldo).replace(',','.'))
            else:
                print_saldo = '-'
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet">
									    <td colspan='3'>Jumlah Pemasukan Zakat Shadaqah Infaq</td>
                                        <td class="text-center">Rp</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(print_saldo)
                                    )

        if next_order_no:
            credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False, order_no__lte = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        if credit_gl:
            for index, list_item in enumerate(credit_gl):
                no_loop += 1
                if(list_item.credit):
                    saldo = 'Rp '+str('{:,}'.format(list_item.credit).replace(',','.'))
                    credit_saldo += list_item.credit
                else:
                    saldo = '-'
                    credit_saldo += 0

                content_table += mark_safe(
                                    '''
                                    <tr>
									    <td>%s</td>
									    <td>%s</td>
									    <td class="text-center">%s</td>
                                        <td class="text-center">Rp</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(no_loop, list_item.transaction, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), saldo)
                                    )

            if(credit_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
            else:
                print_saldo = '-'

            content_table += mark_safe(
                                '''
                                <tr class="bg-credit">
								    <td colspan='3'>Jumlah Pengeluaran Zakat Shadaqah Infaq</td>
                                    <td class="text-center">Rp</td>
								    <td class="text-right">
									    %s
								    </td>
							    </tr>
                                '''%(print_saldo)
                                )
                        
        saldo_akhir = debet_saldo - credit_saldo
        if saldo_akhir:
            saldo_akhir = 'Rp '+str('{:,}'.format(saldo_akhir).replace(',','.'))
        else:
            saldo_akhir = '-'

        content_table += mark_safe(
                                    '''
                                    <tr class="bg-saldo-akhir">
									    <td colspan='3'>Saldo Akhir Zakat Shadaqah Infaq</td>
                                        <td class="text-center">Rp</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(saldo_akhir)
                                    )

        end_table = mark_safe(
                                '''</tbody></table>''')

        content_html += start_table + content_table + end_table

        khutbah = KhutbahJumat.objects.filter(date__date = end_date_format).last()
        if khutbah:
            imam = khutbah.imam
            bilal = khutbah.bilal
        else:
            imam = ''
            bilal = ''
    
        context = {'title':title,
                   'sub_title':sub_title,
                   'content_html':content_html,
                   'imam':imam,
                   'bilal':bilal,
                   'jadwal_sholat':jadwal_sholat,
                   }

        return render(request,'file4print/print_kegiatan_akuntasi.html',context)
    else:
        data = 'Tidak berhasil'
        return JsonResponse(data)

def print_keuangan_zakat(request, start_date, end_date, pass_code):
    assert isinstance(request, HttpRequest)
    if pass_code == 'masjidnuok':
        start_date_format = datetime.strptime(start_date,'%d-%m-%Y').astimezone(current_tzinfo)
        end_date_format = datetime.strptime(end_date,'%d-%m-%Y').astimezone(current_tzinfo)
        year = int(str(end_date_format.year))
        month = int(str(end_date_format.month))
        month_indo = str(bulan_indo(month))
        date = int(str(end_date_format.day))

        hijri_date = Gregorian(year, month, date).to_hijri()
        hijri_date_day = hijri_date.day
        hijri_date_month = hijri_date.month_name()
        hijri_date_month_indo = bulan_hijriah_indo(hijri_date.month)
        hijri_date_year = hijri_date.year

        title = "LAPORAN KEUANGAN ZAKAT SHADAQAH INFAQ MASJID AR-RAUDAH"
        sub_title = 'TANGGAL '+ str(date) +' '+ str(month_indo).upper() +' '+ str(year) +' BERTEPATAN DENGAN '+str(hijri_date_day) +' '+ str(hijri_date_month_indo).upper() +' '+str(hijri_date_year)+' Hijriah'

        content_html = ''

        credit_saldo = 0
        debet_saldo = 0

        start_table = mark_safe(  
                        '''<table class="table mb-0" id="datatable-rekening">
                        <thead>
                            <tr>
                                <th width='5%'>No</th>
					            <th width='10%' data-priority='1'>Tanggal</th>
                                <th width='15%'>Nama</th>
						        <th width='15%' data-priority='2'>Informasi</th>
                                <th width='10%' data-priority='4'>Beras</th>
						        <th width='15%' data-priority='5'>Debet</th>
						        <th width='15%' data-priority='6'>Kredit</th>
						        <th width='15%' data-priority='3'>Saldo</th>
                            </tr>
                        <thead>
                        <tbody>
                        ''')

        content_table = ''

        if start_date_format:
            #minggu_sebelumnya = start_date_format - timedelta(days=7)
            #coa_last_point = ChartOfAccount.objects.get(account_name = 'Gaji dan Tunjangan')
            last_saldo = KegiatanJurnal.objects.filter(date__date = start_date_format, status='Saldo Akhir', is_active = True).last()
            #week_journal = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            week_journal = KegiatanAkuntasi.objects.filter(date__date = start_date_format).order_by('date','id')

            if week_journal.last():
                exclude_transaction = week_journal.last()
                saldo_sebelumnya = week_journal.first().balance
                saldo_sebelumnya2 = week_journal.first().debet
            else:
                saldo_sebelumnya = 0
                saldo_sebelumnya2 = 0

            # if(saldo_sebelumnya):
            #     print_saldo = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
            #     # print_beras =  str('{:,}'.format(exclude_transaction.beras).replace(',','.'))   + ' kg'
            #     # debet_saldo += saldo_sebelumnya
            #     debet_print = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
            # else:
            #     print_saldo = '-'
            #     debet_print = 'Rp 0'
            #     # print_beras = '-'

                
            # if exclude_transaction.beras is not None:
            #     print_beras = str('{:,}'.format(exclude_transaction.beras).replace(',', '.')) + ' kg'
            # else:
            #     print_beras = '-'  # Handle the case when exclude_transaction.beras is None
                
            # # next_order_no = KegiatanJurnal.objects.filter(gl_order_no__gt=exclude_transaction.order_no).first()
            # # Your other code here
        
            next_order_no = KegiatanJurnal.objects.filter(gl_order_no__gt = exclude_transaction.order_no).first()

            # content_table += mark_safe(
            #                     '''
            #                     <tr>
			# 					    <td>%s</td>
            #                         <td class="text-center">%s</td>
            #                         <td>%s</td>
			# 					    <td>%s</td>
            #                         <td class="text-center">%s</td>
			# 					    <td class="text-right">%s</td>
            #                         <td class="text-right">-</td>
			# 					    <td class="text-right">%s</td>
			# 				    </tr>
            #                     '''%(1, 
            #                          start_date_format.astimezone(current_tzinfo).strftime("%d %b %Y"),exclude_transaction.name,
            #                          exclude_transaction.transaction, print_beras, debet_print, print_saldo)
            #                     )


        if next_order_no:
            # debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point).order_by('date','id')
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False).order_by('date')
        else:
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False).order_by('date')
        
        no_loop = 0
        if debet_gl :
            for index, list_item in enumerate(debet_gl):
                no_loop += 1
                if(list_item.debet):
                    saldo = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                    debet_saldo += list_item.debet
                    debet_print = 'Rp '+str('{:,}'.format(debet_saldo + saldo_sebelumnya - saldo_sebelumnya2 ).replace(',','.'))
                    # print_beras =  str('{:,}'.format(list_item.debet).replace(',','.')) + 'kg'
                else:
                    saldo = '-'
                    debet_saldo += 0
                    debet_print = 'Rp 0'
                    # print_beras = '0 kg'
                if(list_item.beras):
                   print_beras =  str('{:,}'.format(list_item.beras).replace(',','.')) + ' kg'
                else:
                    print_beras = '-'

                content_table += mark_safe(
                                    '''
                                      <tr>
                                        <td>%s</td>
                                        <td class="text-center">%s</td>
                                        <td class="text-left">%s</td>
                                        <td class="text-left">%s</td>
                                        <td class="text-center">%s</td>
                                        <td class="text-right">%s</td>
                                        <td class="text-right">-</td>
                                        <td class="text-right">%s</td>
                                    </tr>
                                    '''%(no_loop,
                                         list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"),list_item.name,
                                         list_item.transaction, print_beras, saldo, debet_print)
                                    )

            if(debet_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(debet_saldo + saldo_sebelumnya - saldo_sebelumnya2).replace(',','.'))
            else:
                print_saldo = '-'
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet">
									    <td colspan='7'>Jumlah Pemasukan Zakat Shadaqah Infaq</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(print_saldo)
                                    )

        if next_order_no:
            credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False).order_by('date')
        else:
            credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False).order_by('date')
        if credit_gl:
            for index, list_item in enumerate(credit_gl):
                no_loop += 1
                if(list_item.credit):
                    saldo = 'Rp '+str('{:,}'.format(list_item.credit).replace(',','.'))
                    credit_saldo += list_item.credit
                    credit_print = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
                else:
                    saldo = '-'
                    credit_saldo += 0
                    credit_print = 'Rp 0'
                if(list_item.beras):
                   print_beras =  str('{:,}'.format(list_item.beras).replace(',','.')) + ' kg'
                else:
                    print_beras = '-'

                content_table += mark_safe(
                                    '''
                                    <tr>
									    <td>%s</td>
                                        <td class="text-center">%s</td>
                                        <td class="text-left">%s</td>
                                        <td class="text-left">%s</td>
                                        <td class="text-center">%s</td>
                                        <td class="text-right">-</td>
                                        <td class="text-right">%s</td>
                                        <td class="text-right">%s</td>
								    </tr>
                                    '''%(no_loop, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), list_item.transaction, list_item.name, print_beras, saldo, credit_print)
                                    )

            if(credit_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
            else:
                print_saldo = '-'

            content_table += mark_safe(
                                '''
                                <tr class="bg-credit">
								    <td colspan='7'>Jumlah Pengeluaran Zakat Shadaqah Infaq</td>
								    <td class="text-right">
									    %s
								    </td>
							    </tr>
                                '''%(print_saldo)
                                )
                        
        saldo_akhir = (saldo_sebelumnya + debet_saldo - saldo_sebelumnya2) - credit_saldo
        if saldo_akhir:
            saldo_akhir = 'Rp '+str('{:,}'.format(saldo_akhir).replace(',','.'))
        else:
            saldo_akhir = '-'

        content_table += mark_safe(
                                    '''
                                    <tr class="bg-saldo-akhir">
									    <td colspan='7'>Saldo Akhir Zakat Shadaqah Infaq</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(saldo_akhir)
                                    )

        end_table = mark_safe(
                                '''</tbody></table>''')

        content_html += start_table + content_table + end_table
        
        rekening_list = RekeningMasjid.objects.all().order_by('id')
        rekening = RekeningMasjid.objects.filter(is_primary = True).first()
        rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()
    
        context = {'title':title,
                   'sub_title':sub_title,
                   'content_html':content_html,
                   'rekening_list':rekening_list,
                   'rekening':rekening,
                   'rekening_attachment':rekening_attachment,
                   }

        return render(request,'file4print/print_keuangan_kegiatan.html',context)
    else:
        data = 'Tidak berhasil'
        return JsonResponse(data)
    

def print_ringkasan_zakat(request, start_date, end_date, pass_code):
    assert isinstance(request, HttpRequest)
    if pass_code == 'masjidnuok':
        start_date_format = datetime.strptime(start_date,'%d-%m-%Y').astimezone(current_tzinfo)
        end_date_format = datetime.strptime(end_date,'%d-%m-%Y').astimezone(current_tzinfo)
        year = int(str(end_date_format.year))
        month = int(str(end_date_format.month))
        month_indo = str(bulan_indo(month))
        date = int(str(end_date_format.day))

        hijri_date = Gregorian(year, month, date).to_hijri()
        hijri_date_day = hijri_date.day
        hijri_date_month = hijri_date.month_name()
        hijri_date_month_indo = bulan_hijriah_indo(hijri_date.month)
        hijri_date_year = hijri_date.year

        title = "LAPORAN KEUANGAN ZAKAT SHADAQAH INFAQ MASJID AR-RAUDAH"
        sub_title = 'TANGGAL '+ str(date) +' '+ str(month_indo).upper() +' '+ str(year) +' BERTEPATAN DENGAN '+str(hijri_date_day) +' '+ str(hijri_date_month_indo).upper() +' '+str(hijri_date_year)+' Hijriah'

        content_html = ''

        credit_saldo = 0
        debet_beras = 0
        debet_saldo = 0
        debet_saldo2 = 0
        debet_saldo3 = 0

        start_table = mark_safe(  
                        '''<table class="table mb-0" id="datatable-rekening">
                        <thead>
                            <th width='30%'>Informasi</th>
                            <th width='20%'></th>
					            <th width='30%' data-priority='1'>Jiwa</th>
                                <th width='40%'>Jumlah</th>
                        <thead>
                        <tbody>
                        ''')

        content_table = ''

        if start_date_format:
            #minggu_sebelumnya = start_date_format - timedelta(days=7)
            coa_last_point = ChartOfAccounts.objects.get(account_name = 'Pendapatan Zakat Fitrah')
            coa_last_point_mal = ChartOfAccounts.objects.get(account_name = 'Pendapatan Zakat Maal')
            coa_last_point_fidyah = ChartOfAccounts.objects.get(account_name = 'Pendapatan Zakat Fidyah')
            coa_last_point_infaq = ChartOfAccounts.objects.get(account_name = 'Pendapatan Infaq')
            # last_saldo = KegiatanJurnal.objects.filter(date__date = start_date_format, status='Saldo Akhir', is_active = True).last()
            week_journal = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            week_journal2 = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point_mal).order_by('date','id')
            # week_journal = KegiatanAkuntasi.objects.filter(order_no = last_saldo.gl_order_no).order_by('date','id')
            # ticket_transaction_adult = TicketTransaction.objects.filter(transaction=trans,is_adult=True).values('product__product_name','product','price').annotate(quantity=Count('product'),sum_price=Sum('price')).order_by('product')
            week_count = KegiatanAkuntasi.objects.filter(date__date = start_date_format,coa__in=[coa_last_point, coa_last_point_mal, coa_last_point_fidyah]).values('debet').annotate(week_count=Count("id")).order_by('date')

            if week_journal2.last():
                exclude_transaction = week_journal.last()
                saldo_sebelumnya = week_journal2.first().debet
            else:
                saldo_sebelumnya = 0

            # if(saldo_sebelumnya):
            #     print_saldo = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
            #     # print_beras =  str('{:,}'.format(exclude_transaction.beras).replace(',','.'))   + ' kg'
            #     # debet_saldo += saldo_sebelumnya
            #     debet_print = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
            # else:
            #     print_saldo = '-'
            #     debet_print = 'Rp 0'
            #     # print_beras = '-'

                
            # if exclude_transaction.beras is not None:
            #     print_beras = str('{:,}'.format(exclude_transaction.beras).replace(',', '.')) + ' kg'
            # else:
            #     print_beras = '-'  # Handle the case when exclude_transaction.beras is None
                
            # next_order_no = KegiatanJurnal.objects.filter(gl_order_no__gt=exclude_transaction.order_no).first()
            # Your other code here
        
            next_order_no = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            next_order_no2 = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point_mal).order_by('date','id')
            next_order_no3 = KegiatanAkuntasi.objects.filter(date__date = start_date_format, coa = coa_last_point_fidyah).order_by('date','id')
            # content_table += mark_safe(
            #                     '''
            #                     <tr>
			# 					    <td>%s</td>
            #                         <td class="text-center">%s</td>
            #                         <td>%s</td>
			# 					    <td>%s</td>
            #                         <td class="text-center">%s</td>
			# 					    <td class="text-right">%s</td>
            #                         <td class="text-right">-</td>
			# 					    <td class="text-right">%s</td>
			# 				    </tr>
            #                     '''%(1, 
            #                          start_date_format.astimezone(current_tzinfo).strftime("%d %b %Y"),exclude_transaction.name,
            #                          exclude_transaction.transaction, print_beras, debet_print, print_saldo)
            #                     )
            coa_last_point_with_count = ChartOfAccounts.objects.annotate(
                kegiatanakuntasi_count=Count('kegiatanakuntasi')
            ).get(account_name='Pendapatan Zakat Fitrah')

            coa_last_point_with_count2 = ChartOfAccounts.objects.annotate(
            kegiatanakuntasi_count2=Count('kegiatanakuntasi', filter=~Q(kegiatanakuntasi__beras__isnull=True))
        ).get(account_name='Pendapatan Zakat Fitrah')
            
            coa_fix_last_point = coa_last_point_with_count.kegiatanakuntasi_count - coa_last_point_with_count2.kegiatanakuntasi_count2
            total_beras_sum = KegiatanAkuntasi.objects.filter(coa=coa_last_point_with_count2).aggregate(total_beras_sum=Sum('beras'))['total_beras_sum']
            # total_beras_sum = 469.5

            coa_last_point_with_count_mal = ChartOfAccounts.objects.annotate(
                kegiatanakuntasi_count_mal=Count('kegiatanakuntasi')
            ).get(account_name='Pendapatan Zakat Maal')

            coa_last_point_with_count2_mal = ChartOfAccounts.objects.annotate(
            kegiatanakuntasi_count2_mal=Count('kegiatanakuntasi', filter=~Q(kegiatanakuntasi__beras__isnull=True))
        ).get(account_name='Pendapatan Zakat Maal')
            
            coa_fix_last_point2 = coa_last_point_with_count_mal.kegiatanakuntasi_count_mal 
            total_beras_sum2 = KegiatanAkuntasi.objects.filter(coa=coa_last_point_with_count2_mal).aggregate(total_beras_sum=Sum('beras'))['total_beras_sum']

        coa_last_point_with_count_fidyah = ChartOfAccounts.objects.annotate(
                kegiatanakuntasi_count_fidyah=Count('kegiatanakuntasi')
            ).get(account_name='Pendapatan Zakat Fidyah')

        coa_last_point_with_count2_fidyah = ChartOfAccounts.objects.annotate(
            kegiatanakuntasi_count2_fidyah=Count('kegiatanakuntasi', filter=~Q(kegiatanakuntasi__beras__isnull=True))
        ).get(account_name='Pendapatan Zakat Fidyah')

        coa_last_point_with_count_infaq = ChartOfAccounts.objects.annotate(
                kegiatanakuntasi_count_infaq=Count('kegiatanakuntasi')
            ).get(account_name='Pendapatan Infaq')
        coa_fix_last_point_infaq = coa_last_point_with_count_infaq.kegiatanakuntasi_count_infaq
        total_infaq_sum = KegiatanAkuntasi.objects.filter(coa=coa_last_point_with_count_infaq).aggregate(total_infaq_sum=Sum('debet'))['total_infaq_sum']
        formatted_total_infaq_sum = 'Rp '+str('{:,}'.format(total_infaq_sum).replace(',','.'))   

        coa_fix_last_point3 = coa_last_point_with_count_fidyah.kegiatanakuntasi_count_fidyah 
        total_beras_sum3 = KegiatanAkuntasi.objects.filter(coa=coa_last_point_with_count2_fidyah).aggregate(total_beras_sum=Sum('beras'))['total_beras_sum']

        if next_order_no:
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_with_count).order_by('date','id')
        else:
            debet_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_with_count).order_by('date','id')
        
        no_loop = 0
        if debet_gl :
            for index, list_item in enumerate(debet_gl):
                no_loop += 1
                if(list_item.debet):
                    
                    saldo = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                    debet_saldo += list_item.debet
                
                    debet_print = 'Rp '+str('{:,}'.format(debet_saldo).replace(',','.'))
                    # print_beras =  str('{:,}'.format(list_item.debet).replace(',','.')) + 'kg'
                else:
                    saldo = '-'
                    debet_saldo += 0
                    debet_beras += 0
                    debet_print = 'Rp 0'
                    # print_beras = '0 kg'
                if(debet_beras):
                   debet_beras += list_item.beras
                   print_beras =  str('{:,}'.format(list_item.beras + list_item.beras).replace(',','.')) + ' kg'
                else:
                   print_beras = '-'

                # content_table += mark_safe(
                #                     '''
                #                       <tr>
                #                         <td>%s</td>
                #                         <td class="text-center">%s</td>
                #                         <td class="text-center">%s</td>
                                        
                                        
                #                     </tr>
                #                     '''%(no_loop,coa_last_point_with_count.kegiatanakuntasi_count,coa_last_point_with_count2.kegiatanakuntasi_count2
                #                          )
                #                     )

            if(debet_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(debet_saldo).replace(',','.'))
            else:
                print_saldo = '-'

            # if(debet_saldo):
            #     print_saldo = 'Rp '+str('{:,}'.format(33220000).replace(',','.'))
            # else:
            #     print_saldo = '-'

            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet">
									    <td colspan='2'>Jumlah Pemasukan Zakat Fitrah</td>
									    <td class="text-left">
										    %s
									    </td>
                                        
                                        <td class="text-right">
										    %s
									    </td>
                                         
								    </tr>
                                    '''%(coa_fix_last_point,print_saldo)
                                    )
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet">
									    <td colspan='2'>Jumlah Pemasukan Beras Zakat Fitrah</td>
									    <td class="text-left">
										    %s
									    </td>
                                        
                                        <td class="text-right">
										    %s kg
									    </td>
                                         
								    </tr>
                                    '''%(coa_last_point_with_count2.kegiatanakuntasi_count2,total_beras_sum)
                                    )

        if next_order_no2:
            debet_gl2 = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_mal).order_by('date','id')
        else:
            debet_gl2 = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_mal).order_by('date','id')
        
        no_loop = 0
        if debet_gl2 :
            for index, list_item2 in enumerate(debet_gl2):
                no_loop += 1
                if(list_item2.debet):
                    saldo2 = 'Rp '+str('{:,}'.format(list_item2.debet).replace(',','.'))
                    debet_saldo2 += list_item2.debet
                    debet_print2 = 'Rp '+str('{:,}'.format(debet_saldo2).replace(',','.'))
                    # print_beras =  str('{:,}'.format(list_item.debet).replace(',','.')) + 'kg'
                else:
                    saldo2 = '-'
                    debet_saldo2 += 0
                    debet_print2 = 'Rp 0'
                    # print_beras = '0 kg'
                if(list_item2.beras):
                   print_beras2 =  str('{:,}'.format(list_item2.beras).replace(',','.')) + ' kg'
                else:
                    print_beras2 = '-'

                # content_table += mark_safe(
                #                     '''
                #                       <tr>
                #                         <td>%s</td>
                #                         <td class="text-center">%s</td>
                #                         <td class="text-left">%s</td>
                #                         <td class="text-left">%s</td>
                #                         <td class="text-center">%s</td>
                #                         <td class="text-right">%s</td>
                #                         <td class="text-right">-</td>
                #                         <td class="text-right">%s</td>
                #                     </tr>
                #                     '''%(no_loop,
                #                          list_item2.date.astimezone(current_tzinfo).strftime("%d %b %Y"),list_item2.name,
                #                          list_item2.transaction, print_beras2, saldo2, debet_print2)
                #                     )

            if(debet_saldo2):
                print_saldo2 = 'Rp '+str('{:,}'.format(debet_saldo2).replace(',','.'))
            else:
                print_saldo2 = '-'

            # if(debet_saldo2):
            #     print_saldo2 = 'Rp '+str('{:,}'.format(5000000).replace(',','.'))
            # else:
            #     print_saldo2 = '-'

            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet-mal">
									    <td colspan='2'>Jumlah Pemasukan Zakat Maal </td>
									    <td class="text-left">
										    %s
									    </td>
                                        
                                        <td class="text-right">
										    %s
									    </td>
                                         
								    </tr>
                                    '''%(coa_fix_last_point2,print_saldo2)
                                    )
            
            # content_table += mark_safe(
            #                         '''
            #                         <tr class="bg-debet-mal">
			# 						    <td colspan='2'>Jumlah Pemasukan Zakat Maal </td>
			# 						    <td class="text-left">
			# 							    %s
			# 						    </td>
                                        
            #                             <td class="text-right">
			# 							    %s
			# 						    </td>
                                         
			# 					    </tr>
            #                         '''%(3,print_saldo2)
            #                         )

            # content_table += mark_safe(
            #                         '''
            #                         <tr class="bg-debet-mal">
			# 						    <td colspan='2'>Jumlah Pemasukan Beras Zakat Maal</td>
			# 						    <td class="text-left">
			# 							    %s
			# 						    </td>
                                        
            #                             <td class="text-right">
			# 							    %s kg
			# 						    </td>
                                         
			# 					    </tr>
            #                         '''%(coa_last_point_with_count2_mal.kegiatanakuntasi_count2_mal,total_beras_sum2)
            #                         )
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet-fidyah">
									    <td colspan='2'>Jumlah Pemasukan Infaq Shadaqah </td>
									    <td class="text-left">
										    %s
									    </td>
                                        
                                        <td class="text-right">
										    %s
									    </td>
                                         
								    </tr>
                                    '''%(coa_fix_last_point_infaq,formatted_total_infaq_sum)
                                    )
            


        if next_order_no3:
            debet_gl3 = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_fidyah).order_by('date','id')
        else:
            debet_gl3 = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point_fidyah).order_by('date','id')
        
        no_loop = 0
        if debet_gl3 :
            for index, list_item3 in enumerate(debet_gl3):
                no_loop += 1
                if(list_item3.debet):
                    saldo3 = 'Rp '+str('{:,}'.format(list_item3.debet).replace(',','.'))
                    debet_saldo3 += list_item3.debet
                    debet_print3 = 'Rp '+str('{:,}'.format(debet_saldo3).replace(',','.'))
                    # print_beras =  str('{:,}'.format(list_item.debet).replace(',','.')) + 'kg'
                else:
                    saldo3 = '-'
                    debet_saldo3 += 0
                    debet_print3 = 'Rp 0'
                    # print_beras = '0 kg'
                if(list_item3.beras):
                   print_beras3 =  str('{:,}'.format(list_item3.beras).replace(',','.')) + ' kg'
                else:
                    print_beras3 = '-'

                # content_table += mark_safe(
                #                     '''
                #                       <tr>
                #                         <td>%s</td>
                #                         <td class="text-center">%s</td>
                #                         <td class="text-left">%s</td>
                #                         <td class="text-left">%s</td>
                #                         <td class="text-center">%s</td>
                #                         <td class="text-right">%s</td>
                #                         <td class="text-right">-</td>
                #                         <td class="text-right">%s</td>
                #                     </tr>
                #                     '''%(no_loop,
                #                          list_item3.date.astimezone(current_tzinfo).strftime("%d %b %Y"),list_item3.name,
                #                          list_item3.transaction, print_beras3, saldo3, debet_print3)
                #                     )

            if(debet_saldo3):
                print_saldo3 = 'Rp '+str('{:,}'.format(debet_saldo3).replace(',','.'))
            else:
                print_saldo3 = '-'
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet-fidyah">
									    <td colspan='2'>Jumlah Pemasukan Zakat Fidyah </td>
									    <td class="text-left">
										    %s
									    </td>
                                        
                                        <td class="text-right">
										    %s
									    </td>
                                         
								    </tr>
                                    '''%(coa_fix_last_point3,print_saldo3)
                                    )
            

            # if(debet_saldo3):
            #     print_saldo3 = 'Rp '+str('{:,}'.format(1845000).replace(',','.'))
            # else:
            #     print_saldo3 = '-'
            # content_table += mark_safe(
            #                         '''
            #                         <tr class="bg-debet-fidyah">
			# 						    <td colspan='2'>Jumlah Pemasukan Zakat Fidyah </td>
			# 						    <td class="text-left">
			# 							    %s
			# 						    </td>
                                        
            #                             <td class="text-right">
			# 							    %s
			# 						    </td>
                                         
			# 					    </tr>
            #                         '''%(3,print_saldo3)
            #                         )

            # content_table += mark_safe(
            #                         '''
            #                         <tr class="bg-debet">
			# 						    <td colspan='2'>Jumlah Pemasukan Beras Zakat Fidyah</td>
			# 						    <td class="text-left">
			# 							    %s
			# 						    </td>
                                        
            #                             <td class="text-right">
			# 							    %s kg
			# 						    </td>
                                         
			# 					    </tr>
            #                         '''%(coa_last_point_with_count2_fidyah.kegiatanakuntasi_count2_fidyah,total_beras_sum3)
            #                         )

        # if next_order_no:
        #     credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point).order_by('date','id')
        # else:
        #     credit_gl = KegiatanAkuntasi.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, coa = coa_last_point).order_by('date','id')
        # if credit_gl:
        #     for index, list_item in enumerate(credit_gl):
        #         no_loop += 1
        #         if(list_item.credit):
        #             saldo = 'Rp '+str('{:,}'.format(list_item.credit).replace(',','.'))
        #             credit_saldo += list_item.credit
        #             credit_print = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
        #         else:
        #             saldo = '-'
        #             credit_saldo += 0
        #             credit_print = 'Rp 0'
        #         if(list_item.beras):
        #            print_beras =  str('{:,}'.format(list_item.beras).replace(',','.')) + ' kg'
        #         else:
        #             print_beras = '-'

        #         content_table += mark_safe(
        #                             '''
        #                             <tr>
		# 							    <td>%s</td>
        #                                 <td class="text-center">%s</td>
        #                                 <td class="text-left">%s</td>
        #                                 <td class="text-left">%s</td>
        #                                 <td class="text-center">%s</td>
        #                                 <td class="text-right">-</td>
        #                                 <td class="text-right">%s</td>
        #                                 <td class="text-right">%s</td>
		# 						    </tr>
        #                             '''%(no_loop, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), list_item.transaction, list_item.name, print_beras, saldo, credit_print)
        #                             )

        #     if(credit_saldo):
        #         print_saldo = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
        #     else:
        #         print_saldo = '-'

        #     content_table += mark_safe(
        #                         '''
        #                         <tr class="bg-credit">
		# 						    <td colspan='7'>Jumlah Pengeluaran Zakat Shadaqah Infaq</td>
		# 						    <td class="text-right">
		# 							    %s
		# 						    </td>
		# 					    </tr>
        #                         '''%(print_saldo)
        #                         )
                        
        # saldo_akhir = (saldo_sebelumnya + debet_saldo) - credit_saldo
        saldo_akhir = (debet_saldo + debet_saldo2) + debet_saldo3 + total_infaq_sum
        if saldo_akhir:
            saldo_akhir = 'Rp '+str('{:,}'.format(saldo_akhir).replace(',','.'))
        else:
            saldo_akhir = '-'

        content_table += mark_safe(
                                    '''
                                    <tr class="bg-saldo-akhir">
									    <td colspan='3'>Saldo Akhir Zakat Fitrah Mal Fidyah Infaq Shadaqah</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(saldo_akhir)
                                    )

        end_table = mark_safe(
                                '''</tbody></table>''')

        content_html += start_table + content_table + end_table
        
        rekening_list = RekeningMasjid.objects.all().order_by('id')
        rekening = RekeningMasjid.objects.filter(is_primary = True).first()
        rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening = rekening).first()
    
        context = {'title':title,
                   'sub_title':sub_title,
                   'content_html':content_html,
                   'rekening_list':rekening_list,
                   'rekening':rekening,
                   'rekening_attachment':rekening_attachment,
                   }

        return render(request,'file4print/print_ringkasan_kegiatan.html',context)
    else:
        data = 'Tidak berhasil'
        return JsonResponse(data)
    
    