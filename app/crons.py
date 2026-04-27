from django.contrib.auth import password_validation as passValidate, authenticate, login as user_login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from pathlib import Path
from django.core import validators,serializers
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.forms import modelformset_factory
from django.db.models import Q, Avg, Sum, Count
from django.db import IntegrityError, transaction, connection
import requests
import json
import random
from django.conf import settings
import os
import re
import hashlib

from datetime import datetime, timedelta
from django.utils import timezone

from finance.models import *
from kegiatan.models import *
#from kegiatan.models import *

current_tzinfo = timezone.get_current_timezone()

import logging
logger = logging.getLogger(__file__)

def update_journal_week():
   with transaction.atomic():
        last_journal = KegiatanJurnal.objects.last()
        #Jika ditemukan transaksi dalam Week Journal
        if last_journal:
            first_date = last_journal.date.astimezone(current_tzinfo).date()
            
            last_trans = KegiatanAkuntasi.objects.filter(date__date__gte = first_date).last()
            if last_trans:
                last_date = last_trans.date.astimezone(current_tzinfo).date()
            else:
                last_date = datetime.now().astimezone(current_tzinfo).date()
            
            order_no = last_journal.gl_order_no
            
        #Jika tidak ditemukan transaksi dalam week journal, maka mulai dari awal
        else:
            first_trans = KegiatanAkuntasi.objects.first()
            
            if first_trans:
                first_date = first_trans.date.astimezone(current_tzinfo).date()
                
                last_trans = KegiatanAkuntasi.objects.filter(date__date__gte = first_date).last()
                last_date = last_trans.date.astimezone(current_tzinfo).date()
                
            else:
                first_date = None
                last_date = None

            order_no = None
            

        if first_date and last_date:
            coa_credit = ChartOfAccounts.objects.get(account_name = 'Beban Operasional')
            coa_debet = ChartOfAccounts.objects.get(account_name = 'Pendapatan')
            
            next_date = first_date
            saldo_sebelumnya= 0
            while(next_date < last_date):
                debet_calc = 0
                credit_calc = 0
                saldo_calc = 0

                if order_no:
                    saldo_items = KegiatanAkuntasi.objects.filter(date__date = next_date, order_no = order_no).order_by('order_no','date')
                    print(first_date)
                    print(saldo_items)
                else:
                    saldo_items = KegiatanAkuntasi.objects.filter(date__date = next_date).order_by('order_no','date')
                    print(first_date)
                    print(saldo_items)

                if saldo_items.last():
                    trans_last_point = saldo_items.last()
                    saldo_sebelumnya = trans_last_point.balance
                else:
                    trans_last_point = None
        
                if trans_last_point:
                    debet_items = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte =last_date, debet__isnull=False, order_no__gt = trans_last_point.order_no).order_by('order_no','date')
                else:
                    debet_items = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte =last_date, debet__isnull=False).order_by('order_no','date')

                for item in debet_items:
                    debet_calc += int(item.debet)

                if trans_last_point:
                    credit_items = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte =last_date, credit__isnull=False, order_no__gt = trans_last_point.order_no).order_by('order_no','date')
                else:
                    credit_items = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte =last_date, credit__isnull=False).order_by('order_no','date')

                for item in credit_items:
                    credit_calc += int(item.credit)

                saldo_calc = saldo_sebelumnya + (debet_calc - credit_calc)

                last_checked_point = KegiatanAkuntasi.objects.filter(date__date__gte = first_date, date__date__lte =last_date, balance = saldo_calc).order_by('order_no','date')
                checked_order_no = last_checked_point.last()
                # order_no = checked_order_no.order_no

                if saldo_calc > 0 and checked_order_no:
                    debet_trans = KegiatanJurnal.objects.filter(date = last_date,
                                                 transaction = 'Jumlah Pemasukan Infaq/Sadaqah',
                                                 coa = coa_debet).last()
                    if debet_trans:
                        debet_trans.debet = debet_calc
                        debet_trans.balance = debet_calc
                        debet_trans.is_active = True
                        debet_trans.status = 'Tetap'
                        debet_trans.gl_order_no = checked_order_no.order_no
                        debet_trans.save()
                    else:
                        debet_trans = KegiatanJurnal.objects.create(date = last_date,
                                                    transaction = 'Jumlah Pemasukan Infaq/Sadaqah',
                                                    coa = coa_debet,
                                                    debet = debet_calc,
                                                    balance = debet_calc,
                                                    gl_order_no = checked_order_no.order_no,
                                                    is_active = True,
                                                    status = 'Tetap',
                                                    )
                                         

                    credit_trans = KegiatanJurnal.objects.filter(date = last_date,
                                                 transaction = 'Jumlah Pengeluaran',
                                                 coa = coa_credit).last()
                    if credit_trans:
                        credit_trans.credit = credit_calc
                        credit_trans.balance = credit_calc
                        credit_trans.is_active = True
                        credit_trans.gl_order_no = checked_order_no.order_no
                        credit_trans.status = 'Tetap'
                        credit_trans.save()
                    else:
                        credit_trans = KegiatanJurnal.objects.create(date = last_date,
                                                 transaction = 'Jumlah Pengeluaran',
                                                 coa = coa_credit,
                                                 credit = credit_calc,
                                                 balance = credit_calc,
                                                 gl_order_no = checked_order_no.order_no,
                                                 is_active = True,
                                                 status = 'Tetap',
                                                 )

                    saldo_trans = KegiatanJurnal.objects.filter(date = last_date,
                                                 transaction = 'Saldo Akhir',
                                                 coa = coa_debet).last()
                    if saldo_trans:
                        saldo_trans.debet = debet_calc
                        saldo_trans.credit = credit_calc
                        saldo_trans.balance = saldo_calc
                        saldo_trans.is_active = True
                        saldo_trans.gl_order_no = checked_order_no.order_no
                        saldo_trans.status = 'Saldo Akhir'
                        saldo_trans.save()
                    else:
                        saldo_trans= KegiatanJurnal.objects.create(date = last_date,
                                                 transaction = 'Saldo Akhir',
                                                 coa = coa_debet,
                                                 debet = debet_calc,
                                                 credit = credit_calc,
                                                 balance = saldo_calc,
                                                 gl_order_no = checked_order_no.order_no,
                                                 is_active = True,
                                                 status = 'Saldo Akhir',
                                                 )

                next_trans = KegiatanAkuntasi.objects.filter(date__date = last_date).order_by('order_no','date').first()
                if next_trans:
                    first_date = next_trans.date.astimezone(current_tzinfo).date()
                    next_date = first_date
                    # last_date = first_date + timedelta(weeks=1)

                    saldo_sebelumnya = saldo_calc
                else:
                    break
        else:
            pass
        

def update_week_journal():
    with transaction.atomic():
        last_journal = WeekJournal.objects.last()
        #Jika ditemukan transaksi dalam Week Journal
        if last_journal:
            first_date = last_journal.date.astimezone(current_tzinfo).date()
            
            selected_friday = first_date + timedelta(weeks=1)
            order_no = 0
            # order_no = last_journal.gl_order_no
        #Jika tidak ditemukan transaksi dalam week journal, maka mulai dari awal
        else:
            first_trans = GeneralLedger.objects.first()
            if first_trans:
                first_date = first_trans.date.astimezone(current_tzinfo).date()
                selected_friday = first_date + timedelta(days=((4-first_date.weekday()) % 7))
            else:
                first_date = None
                selected_friday = None
            order_no = 0

        if first_date and selected_friday:
            today = datetime.now().astimezone(current_tzinfo).date()
            coa_credit = ChartOfAccount.objects.get(account_name = 'Beban Operasional')
            coa_debet = ChartOfAccount.objects.get(account_name = 'Pendapatan')

            saldo_sebelumnya= 0
            while(selected_friday <= today):
                debet_calc = 0
                credit_calc = 0
                saldo_calc = 0

                if order_no:
                    saldo_items = GeneralLedger.objects.filter(date__date = first_date, order_no = order_no).order_by('order_no','date')
                    logger.info(first_date) #2023-11-10
                    logger.info(order_no) #211
                    logger.info(saldo_items)
                else:
                    saldo_items = GeneralLedger.objects.filter(date__date = first_date).order_by('order_no','date')
                    logger.info(first_date)
                    logger.info(saldo_items)

                if saldo_items.last():
                    trans_last_point = saldo_items.last()
                    saldo_sebelumnya = trans_last_point.balance
                else:
                    trans_last_point = None
        
                if trans_last_point:
                    debet_items = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte =selected_friday, debet__isnull=False, order_no__gt = trans_last_point.order_no).order_by('order_no','date')
                else:
                    debet_items = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte =selected_friday, debet__isnull=False).order_by('order_no','date')

                for item in debet_items:
                    debet_calc += int(item.debet)

                if trans_last_point:
                    credit_items = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte =selected_friday, credit__isnull=False, order_no__gt = trans_last_point.order_no).order_by('order_no','date')
                else:
                    credit_items = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte =selected_friday, credit__isnull=False).order_by('order_no','date')

                for item in credit_items:
                    credit_calc += int(item.credit)

                saldo_calc = saldo_sebelumnya + (debet_calc - credit_calc)

                last_checked_point = GeneralLedger.objects.filter(date__date__gte = first_date, date__date__lte =selected_friday, balance = saldo_calc).order_by('order_no','date')
                checked_order_no = last_checked_point.last()
                # order_no = checked_order_no.order_no

                if saldo_calc > 0 and checked_order_no:
                    debet_trans = WeekJournal.objects.filter(date = selected_friday,
                                                 transaction = 'Jumlah Pemasukan Infaq/Sadaqah',
                                                 coa = coa_debet).last()
                    if debet_trans:
                        debet_trans.debet = debet_calc
                        debet_trans.balance = debet_calc
                        debet_trans.is_active = True
                        debet_trans.status = 'Tetap'
                        debet_trans.gl_order_no = checked_order_no.order_no
                        debet_trans.save()
                    else:
                        debet_trans = WeekJournal.objects.create(date = selected_friday,
                                                    transaction = 'Jumlah Pemasukan Infaq/Sadaqah',
                                                    coa = coa_debet,
                                                    debet = debet_calc,
                                                    balance = debet_calc,
                                                    gl_order_no = checked_order_no.order_no,
                                                    is_active = True,
                                                    status = 'Tetap',
                                                    )
                                         

                    credit_trans = WeekJournal.objects.filter(date = selected_friday,
                                                 transaction = 'Jumlah Pengeluaran',
                                                 coa = coa_credit).last()
                    if credit_trans:
                        credit_trans.credit = credit_calc
                        credit_trans.balance = credit_calc
                        credit_trans.is_active = True
                        credit_trans.gl_order_no = checked_order_no.order_no
                        credit_trans.status = 'Tetap'
                        credit_trans.save()
                    else:
                        credit_trans = WeekJournal.objects.create(date = selected_friday,
                                                 transaction = 'Jumlah Pengeluaran',
                                                 coa = coa_credit,
                                                 credit = credit_calc,
                                                 balance = credit_calc,
                                                 gl_order_no = checked_order_no.order_no,
                                                 is_active = True,
                                                 status = 'Tetap',
                                                 )

                    saldo_trans = WeekJournal.objects.filter(date = selected_friday,
                                                 transaction = 'Saldo Akhir',
                                                 coa = coa_debet).last()
                    if saldo_trans:
                        saldo_trans.debet = debet_calc
                        saldo_trans.credit = credit_calc
                        saldo_trans.balance = saldo_calc
                        saldo_trans.is_active = True
                        saldo_trans.gl_order_no = checked_order_no.order_no
                        saldo_trans.status = 'Saldo Akhir'
                        saldo_trans.save()
                    else:
                        saldo_trans= WeekJournal.objects.create(date = selected_friday,
                                                 transaction = 'Saldo Akhir',
                                                 coa = coa_debet,
                                                 debet = debet_calc,
                                                 credit = credit_calc,
                                                 balance = saldo_calc,
                                                 gl_order_no = checked_order_no.order_no,
                                                 is_active = True,
                                                 status = 'Saldo Akhir',
                                                 )

                next_date = GeneralLedger.objects.filter(date__date = selected_friday).order_by('order_no','date').first()
                if next_date:
                    first_date = next_date.date.astimezone(current_tzinfo).date()
                    selected_friday = first_date + timedelta(weeks=1)

                    saldo_sebelumnya = saldo_calc
                else:
                    break
        else:
            pass

    


