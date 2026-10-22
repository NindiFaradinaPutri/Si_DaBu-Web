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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage

import hashlib
from uuid import uuid4
from rest_framework.authtoken.models import Token

from complaint.models import *
from complaint.forms import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def complaint_response_update(request):
    if request.method == 'POST':
        user_id = request.POST.get('user', None)
        status_id = request.POST.get('status', None)
        complaint_id = request.POST.get('complaint_id', None)

        responseForm = ComplaintResponseForm(request.POST)
        user = UserData.objects.filter(id=user_id).first()
        status = ComplaintStatus.objects.filter(id=status_id).first()

        if responseForm.is_valid():
            comment = responseForm.cleaned_data['comment']

            response_list = ComplaintResponse.objects.filter(complaint_id=complaint_id)
            if response_list:
                last_response = response_list.latest('id')
            else:
                last_response = None

            # ✅ FIX: tambah pengecekan status tidak None
            if last_response and last_response.status and status and last_response.status.id == int(status_id):
                last_response.user = user
                last_response.status = status
                last_response.comment = comment
                last_response.save()

                # ✅ FIX: amanin status
                if last_response.status and last_response.status.status != "Open":
                    current_site = get_current_site(request)
                    mail_subject = 'Re: ' + last_response.complaint.subject
                    message = render_to_string('template/complaint_respone.html', {
                        'response': last_response,
                    })
                    to_email = last_response.complaint.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
            else:
                response = ComplaintResponse.objects.create(
                    complaint_id=complaint_id,
                    user=user,
                    status=status,
                    comment=comment
                )

                # ✅ FIX: amanin status
                if response.status and response.status.status != "Open":
                    current_site = get_current_site(request)
                    mail_subject = 'Re: ' + response.complaint.subject
                    message = render_to_string('template/complaint_respone.html', {
                        'response': response,
                    })
                    to_email = response.complaint.email
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()

        # ambil ulang data terbaru
        response_list = ComplaintResponse.objects.filter(complaint_id=complaint_id)
        if response_list:
            response = response_list.latest('id')
        else:
            response = None

        template = 'views/view_complaint_response.html'
        data = {
            'response_list': response_list,
        }

        html = render_to_string(template_name=template, context=data, request=request)

        # ✅ FIX: gunakan variable baru agar tidak kirim object ke JSON
        status_badge = ""

        if response and response.status:
            if response.status.status == 'Open':
                status_badge = "<span class='badge badge-pill badge-success' style='font-size:13px;'>%s</span>" % response.status.status
            elif response.status.status == 'On Progress':
                status_badge = "<span class='badge badge-pill badge-info' style='font-size:13px;'>%s</span>" % response.status.status
            elif response.status.status == 'Pending':
                status_badge = "<span class='badge badge-pill badge-warning' style='font-size:13px;'>%s</span>" % response.status.status
            elif response.status.status == 'Closed':
                status_badge = "<span class='badge badge-pill badge-dark' style='font-size:13px;'>%s</span>" % response.status.status

        context = {
            'html': html,
            'message': 'Response berhasil diupdate',
            'status': status_badge,  # ✅ sudah string
            'date': response.response_date.strftime("%d %B %y, %H:%M") if response else '',
        }

        return JsonResponse(context)