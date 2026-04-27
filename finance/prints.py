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

from finance.models import *
from finance.forms import *
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

def print_khotbah_jumat(request, start_date, end_date, pass_code):
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
            last_saldo = WeekJournal.objects.filter(date__date = start_date_format, status='Saldo Akhir', is_active = True).last()
            
            #week_journal = GeneralLedger.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            week_journal = GeneralLedger.objects.filter(order_no = last_saldo.gl_order_no).order_by('date','id')

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

            next_order_no = WeekJournal.objects.filter(gl_order_no__gt = exclude_transaction.order_no).first()

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
            debet_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, order_no__lt = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            debet_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')

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
									    <td colspan='3'>Jumlah Pemasukan Masjid</td>
                                        <td class="text-center">Rp</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(print_saldo)
                                    )

        if next_order_no:
            credit_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False, order_no__lte = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            credit_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
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
								    <td colspan='3'>Jumlah Pengeluaran Masjid</td>
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
									    <td colspan='3'>Saldo Akhir Masjid</td>
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

        return render(request,'file4print/print_khotbah_jumat.html',context)
    else:
        data = 'Tidak berhasil'
        return JsonResponse(data)

def print_keuangan(request, start_date, end_date, pass_code):
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

        title = "LAPORAN KEUANGAN MASJID AR-RAUDAH"
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
						        <th width='25%' data-priority='2'>Transaksi</th>
						        <th width='10%' data-priority='4'>Debet</th>
						        <th width='10%' data-priority='5'>Kredit</th>
						        <th width='10%' data-priority='3'>Saldo</th>
                            </tr>
                        <thead>
                        <tbody>
                        ''')

        content_table = ''

        if start_date_format:
            #minggu_sebelumnya = start_date_format - timedelta(days=7)
            #coa_last_point = ChartOfAccount.objects.get(account_name = 'Gaji dan Tunjangan')
            last_saldo = WeekJournal.objects.filter(date__date = start_date_format, status='Saldo Akhir', is_active = True).last()
            #week_journal = GeneralLedger.objects.filter(date__date = start_date_format, coa = coa_last_point).order_by('date','id')
            week_journal = GeneralLedger.objects.filter(order_no = last_saldo.gl_order_no).order_by('date','id')

            if week_journal.last():
                exclude_transaction = week_journal.last()
                saldo_sebelumnya = week_journal.last().balance
            else:
                saldo_sebelumnya = 0

            if(saldo_sebelumnya):
                print_saldo = 'Rp '+str('{:,}'.format(saldo_sebelumnya).replace(',','.'))
                #debet_saldo += saldo_sebelumnya
            else:
                print_saldo = '-'

            next_order_no = WeekJournal.objects.filter(gl_order_no__gt = exclude_transaction.order_no).first()

            content_table += mark_safe(
                                '''
                                <tr>
								    <td class="text-left bg-debet" colspan='5'>Saldo Minggu Sebelumnya (%s)</td>
                                    <td class="text-right bg-debet">
									    %s
								    </td>
							    </tr>
                                '''%(
                                     start_date_format.astimezone(current_tzinfo).strftime("%d %b %Y"), 
                                     print_saldo)
                                )


        if next_order_no:
            debet_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False, order_no__lt = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            debet_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, debet__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        
        no_loop = 0
        if debet_gl :
            for index, list_item in enumerate(debet_gl):
                no_loop += 1
                if(list_item.debet):
                    saldo = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                    debet_saldo += list_item.debet
                    debet_print = 'Rp '+str('{:,}'.format(debet_saldo).replace(',','.'))
                else:
                    saldo = '-'
                    debet_saldo += 0
                    debet_print = 'Rp 0'

                content_table += mark_safe(
                                    '''
                                    <tr>
									    <td>%s</td>
                                        <td class="text-center">%s</td>
									    <td class="text-left">%s</td>
									    <td class="text-right">
										    %s
									    </td>
                                        <td class="text-right">-</td>
                                        <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(no_loop,
                                         list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"),
                                         list_item.transaction, saldo,debet_print)
                                    )

            if(debet_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(debet_saldo).replace(',','.'))
            else:
                print_saldo = '-'
            content_table += mark_safe(
                                    '''
                                    <tr class="bg-debet">
									    <td colspan='5'>Jumlah Pemasukan Masjid</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(print_saldo)
                                    )

        if next_order_no:
            credit_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False, order_no__lte = next_order_no.gl_order_no).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
        else:
            credit_gl = GeneralLedger.objects.filter(date__gte = start_date_format, date__lte = end_date_format, credit__isnull = False).exclude(order_no__lte = exclude_transaction.order_no).order_by('date')
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

                content_table += mark_safe(
                                    '''
                                    <tr>
									    <td>%s</td>
                                        <td class="text-center">%s</td>
                                        <td class="text-left">%s</td>
                                        <td class="text-right">-</td>
									    <td class="text-center">%s</td>
									    <td class="text-right">
										    %s
									    </td>
								    </tr>
                                    '''%(no_loop, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), list_item.transaction, saldo, credit_print)
                                    )

            if(credit_saldo):
                print_saldo = 'Rp '+str('{:,}'.format(credit_saldo).replace(',','.'))
            else:
                print_saldo = '-'

            content_table += mark_safe(
                                '''
                                <tr class="bg-credit">
								    <td colspan='5'>Jumlah Pengeluaran Masjid</td>
								    <td class="text-right">
									    %s
								    </td>
							    </tr>
                                '''%(print_saldo)
                                )
                        
        saldo_akhir = (saldo_sebelumnya + debet_saldo) - credit_saldo
        if saldo_akhir:
            saldo_akhir = 'Rp '+str('{:,}'.format(saldo_akhir).replace(',','.'))
        else:
            saldo_akhir = '-'

        content_table += mark_safe(
                                    '''
                                    <tr class="bg-saldo-akhir">
									    <td colspan='5'>Saldo Akhir Masjid</td>
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

        return render(request,'file4print/print_keuangan.html',context)
    else:
        data = 'Tidak berhasil'
        return JsonResponse(data)