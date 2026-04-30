import os
import json
from uuid import uuid4
from datetime import datetime,timedelta
#import pandas as pda
import shutil
from django.conf import settings
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from decimal import Decimal

#from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.db.models import Q
from decimal import Decimal
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext
from django.contrib.auth.password_validation import validate_password, NumericPasswordValidator, CommonPasswordValidator,UserAttributeSimilarityValidator, MinimumLengthValidator
import re
from django.template import RequestContext
from django.template.loader import render_to_string
from collections import Counter
from django_tables2 import RequestConfig
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import status
from rest_framework.response import Response
import re
from django.contrib import messages
import logging
logger = logging.getLogger(__file__)

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#CUSTOM VALIDATORS
class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("Password tidak berisikan (minimal) 1 digit angka (0-9)"),
                code='password_no_number',
            )
    def get_help_text(self):
        return _("Password harus berisikan minimal 1 digit angka (0-9)")

class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("Password tidak berisikan (minimal) 1 huruf besar (A-Z)"),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _("Password harus berisikan minimal 1 huruf besar (A-Z)")

class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("Password tidak berisikan (minimal) 1 huruf kecil (a-z)"),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _("Password harus berisikan minimal 1 huruf kecil (a-z)")

class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("Password harus berisikan minimal 1 simbol (1,;:#?):" +
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Password harus berisikan minimal 1 simbol (1,;:#?):" +
            "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"
        )

class CustomNumericPasswordValidator(NumericPasswordValidator):
    def get_help_text(self):
        return _('Password tidak boleh Angka semua.')

class CustomCommonPasswordValidator(CommonPasswordValidator):
    def get_help_text(self):
        return _('Password anda tidak boleh menggunakan kata umum.')

class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def get_help_text(self):
        return _('Password anda tidak boleh mirip dengan personal informasi lainnya.')

class CustomMinimumLengthValidator(MinimumLengthValidator):
    def get_help_text(self):
        return ngettext(
            "Password anda minimal berjumlah %(min_length)d character.",
            "Password anda minimal berjumlah %(min_length)d characters.",
            self.min_length
        ) % {'min_length': self.min_length}

def encoding_id(code):
    try:
        encode_id = hashid.encode(code)
        return encode_id
    except Exception as err:
        logger.error("Kesalahan dalam proses encoding "+str(err))
        return None

def decoding_id(code):
    try:
        decode_id = hashid.decode(code)[0]
        return decode_id
    except Exception as err:
        logger.error("Kesalahan dalam proses decoding "+str(err))
        return None

def ensure_cookies(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    request.session.set_test_cookie()

def timestamp():
    date= datetime.utcnow() - datetime(1970, 1, 1)
    seconds = (date.total_seconds())
    milliseconds = round(seconds*1000)
    return milliseconds

def bulan_indo(monthNo):
    bulan_indo = ['Januari','Pebruari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'December']

    return bulan_indo[(monthNo-1)]

def bulan_hijriah_indo(monthNo):
    bulanHijriah = ['Muharam','Safar', 'Rabiul Awal', 'Rabiul Akhir', 'Jumadil Awal', 'Jumadil Akhir', 'Rajab', 'Syakban', 'Ramadhan', 'Syawal', 'Zulkaidah', 'Zulhijah']

    return bulanHijriah[(monthNo-1)]

def metadata_api(status_code,message):
    metadata = {'code': status_code,
                'message': message}
    return metadata

def error_method():
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    metadata = {'code': status_code,
                'message': "Method dilarang"}

    context = {"metadata": metadata}
    return Response(context,status=status_code)


def normalize(text):
    """
    Normalisasi:
    - lowercase
    - hapus spasi
    - hapus simbol
    """
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(text).lower())


def find_column(df, keywords):
    """
    Cari kolom berdasarkan keyword fleksibel
    """
    normalized_cols = {
        normalize(col): col for col in df.columns
    }

    for key in keywords:
        key_norm = normalize(key)

        for col_norm, original_col in normalized_cols.items():
            if key_norm in col_norm:
                return original_col

    return None


def format_datetime_indo(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        bulan = [
            "Januari", "Februari", "Maret", "April",
            "Mei", "Juni", "Juli", "Agustus",
            "September", "Oktober", "November", "Desember"
        ]

        return f"{dt.day} {bulan[dt.month-1]} {dt.year}, {dt.strftime('%H:%M')} WIB"
    except:
        return dt_str