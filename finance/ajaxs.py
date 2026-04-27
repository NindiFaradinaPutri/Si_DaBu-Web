from utils.utils import *
from app.decorators import *

import json

from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

import calendar
from django.utils import timezone
current_tzinfo = timezone.get_current_timezone()

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def addform_gl(request):
    if request.method == 'POST':
        gl_count = request.POST.get('gl_count',1)

        glForm = GeneralLedgerForm()
        id_form = 'id_glappend_'+str(int(gl_count)-1)
        id_prefix = 'id_gl-'+str(int(gl_count)-1)
        prefix = 'gl-'+str(int(gl_count)-1)

        context = {
                'id_prefix':id_prefix,
                'prefix':prefix,
                'counter':gl_count,
                'id_form':id_form,
                'form':glForm,
                }
        template = 'template/forms/tmp_table_form_append.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)

def delete_gl(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        #id = decoding_id(raw_id)
        gl = GeneralLedger.objects.filter(id = id).first()

        if(gl):
            gl.delete()

        status = 'transaksi berhasil dihapus'

        return HttpResponse(status)

def addform_week_journal(request):
    if request.method == 'POST':
        journal_count = request.POST.get('gl_count',1)

        journalForm = WeekJournalForm()
        id_form = 'id_journalappend_'+str(int(journal_count)-1)
        id_prefix = 'id_journal-'+str(int(journal_count)-1)
        prefix = 'journal-'+str(int(journal_count)-1)

        context = {
                'id_prefix':id_prefix,
                'prefix':prefix,
                'counter':journal_count,
                'id_form':id_form,
                'form':journalForm,
                }
        template = 'template/forms/tmp_table_form_append.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)        

def delete_week_journal(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        #id = decoding_id(raw_id)
        journal = WeekJournal.objects.filter(id = id).first()

        if(journal):
            journal.is_active = False
            journal.status = 'Dihapus'
            journal.save()

        status = 'transaksi berhasil dihapus'

        return HttpResponse(status)

def filter_gl_by_date(request):
    if request.method == 'POST':
        raw_start_date = request.POST.get('start_date')
        raw_end_date = request.POST.get('end_date')

        start_date = datetime.strptime(raw_start_date,'%d-%m-%Y').astimezone(current_tzinfo)
        end_date = datetime.strptime(raw_end_date,'%d-%m-%Y').astimezone(current_tzinfo)

        data_gl = GeneralLedger.objects.filter(date__gte = start_date, date__lte = end_date).order_by('date')

        start_html = mark_safe(
                            '''<table class="table table-bordered table-striped mb-0" id="datatable-rekening">
							<thead>
								<tr class="text-center">
									<th>No</th>
									<th>Tanggal</th>
									<th>Transaksi</th>
									<th>Debet</th>
									<th>Kredit</th>
									<th>Saldo</th>
								</tr>
							</thead><tbody>''')

        content_html = mark_safe('')

        end_html = mark_safe(
                            '''</tbody></table>''')

        if data_gl:
            for index, list_item in enumerate(data_gl):
                index += 1
                if(list_item.debet):
                    debet = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                else:
                    debet = '-'

                if(list_item.credit):
                    kredit = 'Rp '+str('{:,}'.format(list_item.credit).replace(',','.'))
                else:
                    kredit = '-'

                if(list_item.balance):
                    balance = 'Rp '+str('{:,}'.format(list_item.balance).replace(',','.'))
                else:
                    balance = '-'

                content_html += mark_safe(
                                '''
                                <tr>
									<td>%s</td>
									<td>%s</td>
									<td>%s</td>
									<td class="text-right">
										%s
									</td>
									<td class="text-right">
										%s
									</td>
									<td class="text-right">
										%s
									</td>
								</tr>
                                '''%(index, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), list_item.transaction, debet, kredit, balance)
                                )

            html = start_html + content_html + end_html
        else:
            html = ''
        
        data = {
                'html':html,
                'start_date':start_date.strftime('%d %b %Y'),
                'end_date':end_date.strftime('%d %b %Y'),
                'start_date_format':start_date.strftime('%d-%m-%Y'),
                'end_date_format':end_date.strftime('%d-%m-%Y'),
                }

        return JsonResponse(data)

def filter_gl_by_month(request):
    if request.method == 'POST':
        raw_month = request.POST.get('month')

        selected_month = datetime.strptime(raw_month,'%m-%Y')

        data_gl = GeneralLedger.objects.filter(date__month = selected_month.month, date__year = selected_month.year).order_by('date')
        
        start_date = selected_month.astimezone(current_tzinfo).replace(day=1)
        range_date = calendar.monthrange(selected_month.year, selected_month.month)
        end_date = selected_month.astimezone(current_tzinfo).replace(day=range_date[1])

        start_html = mark_safe(
                            '''<table class="table table-bordered table-striped mb-0" id="datatable-rekening">
							<thead>
								<tr class="text-center">
									<th>No</th>
									<th>Tanggal</th>
									<th>Transaksi</th>
									<th>Debet</th>
									<th>Kredit</th>
									<th>Saldo</th>
								</tr>
							</thead><tbody>''')

        content_html = mark_safe('')

        end_html = mark_safe(
                            '''</tbody></table>''')

        if data_gl:
            for index, list_item in enumerate(data_gl):
                index += 1
                if(list_item.debet):
                    debet = 'Rp '+str('{:,}'.format(list_item.debet).replace(',','.'))
                else:
                    debet = '-'

                if(list_item.credit):
                    kredit = 'Rp '+str('{:,}'.format(list_item.credit).replace(',','.'))
                else:
                    kredit = '-'

                if(list_item.balance):
                    balance = 'Rp '+str('{:,}'.format(list_item.balance).replace(',','.'))
                else:
                    balance = '-'

                content_html += mark_safe(
                                '''
                                <tr>
									<td>%s</td>
									<td>%s</td>
									<td>%s</td>
									<td class="text-right">
										%s
									</td>
									<td class="text-right">
										%s
									</td>
									<td class="text-right">
										%s
									</td>
								</tr>
                                '''%(index, list_item.date.astimezone(current_tzinfo).strftime("%d %b %Y"), list_item.transaction, debet, kredit, balance)
                                )

            html = start_html + content_html + end_html
        else:
            html = ''

        data = {
                'html':html,
                'start_date':start_date.strftime('%d %b %Y'),
                'end_date':end_date.strftime('%d %b %Y'),
                'start_date_format':start_date.strftime('%d-%m-%Y'),
                'end_date_format':end_date.strftime('%d-%m-%Y'),
                }

        return JsonResponse(data)