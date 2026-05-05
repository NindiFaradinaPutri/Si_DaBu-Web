import os
import json
from uuid import uuid4
from datetime import datetime,timedelta
#import pandas as pda
import shutil
import urllib.parse
from django.conf import settings
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from decimal import Decimal

#from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.db.models import Q, F 
from decimal import Decimal
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _, ngettext
from django.contrib.auth.password_validation import validate_password, NumericPasswordValidator, CommonPasswordValidator,UserAttributeSimilarityValidator, MinimumLengthValidator
import re
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from qrcode import make
from django.core.files import File
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from io import BytesIO
from xhtml2pdf import pisa
from django.core.files.base import ContentFile
from collections import Counter
from django_tables2 import RequestConfig
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from event.models import *
from form.models import FormResponse
from participant.models import *
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
    


def extract_maps_url(url):
    if not url:
        return ""

    # ambil koordinat
    coord_match = re.search(r'!2d([-\d.]+)!3d([-\d.]+)', url)

    # ambil nama tempat
    name_match = re.search(r'!2s([^!]+)', url)

    lat, lng, name = None, None, None

    if coord_match:
        lng = coord_match.group(1)
        lat = coord_match.group(2)

    if name_match:
        name = urllib.parse.unquote(name_match.group(1))

    # 🔥 PRIORITAS: nama + koordinat
    if name and lat and lng:
        name_clean = name.replace(" ", "+")
        return f"https://www.google.com/maps?q={name_clean}@{lat},{lng}"

    # fallback ke koordinat
    if lat and lng:
        return f"https://www.google.com/maps?ll={lat},{lng}&q={lat},{lng}&z=17"

    # fallback terakhir
    return url.split('"')[0]
    
def generate_pdf(html):
    result = BytesIO()
    pisa.CreatePDF(html, dest=result)
    return result.getvalue()

def create_and_send_qremail(request, event_id):
    event = Event.objects.filter(id = event_id).first()
    participant = Participant.objects.filter(id_event = event)

    current_site = get_current_site(request)
    mail_subject = '[PrensenGO] Your ticket for ' + event.name

    for p in participant:
        if not p.qr_code:
            qr_data = f"{event.unique_name},{p.unique_user}"

            img = make(qr_data)

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f"{event.unique_name}_{p.unique_user}.png"

            p.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
            p.save()

        url = request.build_absolute_uri(participant.first().qr_code.url)

        instansi_obj = FormResponse.objects.annotate(
            instansi=F("data_response__excel_data__Instansi (Jika ada)")
            ).filter(participant=p).first()

        instansi_value = getattr(instansi_obj, 'instansi', '')
        
        current_site = get_current_site(request)

        message = render_to_string('template/registrations/attende_qrcode.html', {
            'event': event,
            'domain': current_site.domain,
            'qr_code': url,
            'instansi': instansi_value or '-',
            'participant':participant.first(),
        })
        plain_message = strip_tags(message)
        to_email = p.email
        email = EmailMultiAlternatives(
            subject=mail_subject,
            body=plain_message,
            from_email=None,
            to=[to_email]
        )
        message_pdf = render_to_string('template/registrations/attende_qrcode_pdf.html', {
            'event': event,
            'domain': current_site.domain,
            'qr_code': url,
            'instansi': instansi.instansi,
            'participant':participant.first(),
        })
        pdf = generate_pdf(message_pdf)
        email.attach_alternative(message, "text/html")
        email.attach(event.name+" ticket.pdf", pdf, "application/pdf")
        email.send()