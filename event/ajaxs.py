from participant.models import Participant, StatusParticipant
from utils.utils import *
from app.decorators import *
import numpy as np

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
from django.views.decorators.csrf import csrf_exempt
from authentication.models import *
from form.models import *
from authentication.forms import *

from banner.models import *
import pandas as pd
import json
from banner.filters import *
# from banner.ads_forms import *

#Set Loggin
import logging
logger = logging.getLogger(__file__)

def filter_gallery(request):
    if request.method == 'POST':
        gallery_query = Gallery.objects.all().order_by('-id')

        page = request.POST.get('page')
        per_page = request.POST.get('per_page')
        sort_by = request.POST.get('sort_by')

# @csrf_exempt
# def upload_participant(request):
#     if request.method == "POST":

#         uploaded_file = request.FILES.get("excelFile")

#         if not uploaded_file:
#             return JsonResponse({
#                 "status": "failed",
#                 "message": "File tidak ditemukan"
#             })

#         try:
#             file_name = uploaded_file.name.lower()

#             # =========================
#             # READ EXCEL / CSV
#             # =========================
#             if file_name.endswith(".csv"):
#                 df = pd.read_csv(uploaded_file)

#             elif file_name.endswith(".xlsx"):
#                 df = pd.read_excel(
#                     uploaded_file,
#                     engine="openpyxl"
#                 )

#             elif file_name.endswith(".xls"):
#                 df = pd.read_excel(
#                     uploaded_file,
#                     engine="xlrd"
#                 )

#             else:
#                 return JsonResponse({
#                     "status": "failed",
#                     "message": "Format file tidak didukung"
#                 })

#             # convert dataframe to list json
#             df = df.fillna("")

#             # convert timestamp/date columns
#             for col in df.columns:
#                 df[col] = df[col].apply(
#                     lambda x: x.strftime("%Y-%m-%d %H:%M:%S")
#                     if isinstance(x, pd.Timestamp)
#                     else x
#                 )

#             excel_json = df.to_dict(orient="records")

#             # ambil form
#             form_obj = Form.objects.first()

#             # =========================
#             # SAVE RAW JSON
#             # =========================
#             form_response = FormResponse.objects.create(
#                 form=form_obj,
#                 data_response=excel_json
#             )

#             # =========================
#             # SAVE PARTICIPANTS
#             # =========================
#             for row in excel_json:
#                 Participant.objects.create(
#                     form=form_obj,
#                     name=row.get("name") or row.get("Name"),
#                     email=row.get("email") or row.get("Email"),
#                     phone=row.get("phone") or row.get("Phone")
#                 )

#             return JsonResponse({
#                 "status": "success",
#                 "message": "Upload berhasil dan participant tersimpan",
#                 "form_response_id": form_response.id
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "status": "failed",
#                 "message": str(e)
#             })

#     return JsonResponse({
#         "status": "failed",
#         "message": "Invalid request"
#     })



@csrf_exempt
def upload_participant(request):

    if request.method != "POST":
        return JsonResponse({
            "status": "failed",
            "message": "Invalid request"
        })

    uploaded_file = request.FILES.get("excelFile")
    event_id = request.POST.get("event_id")

    if not uploaded_file:
        return JsonResponse({
            "status": "failed",
            "message": "File tidak ditemukan"
        })

    if not event_id:
        return JsonResponse({
            "status": "failed",
            "message": "Event tidak ditemukan"
        })

    try:
        event = Event.objects.get(id=event_id)
        status_default = StatusParticipant.objects.get(id=3)

        file_name = uploaded_file.name.lower()

        # =========================
        # READ FILE
        # =========================
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        elif file_name.endswith(".xls"):
            df = pd.read_excel(uploaded_file, engine="xlrd")

        else:
            return JsonResponse({
                "status": "failed",
                "message": "Format file tidak didukung"
            })

        # =========================
        # CLEAN DATA
        # =========================
        def clean_value(val):
            bulan = [
                "Januari", "Februari", "Maret", "April",
                "Mei", "Juni", "Juli", "Agustus",
                "September", "Oktober", "November", "Desember"
            ]

            if isinstance(val, pd.Timestamp):
                dt = val.to_pydatetime()

                # 🔥 KONVERSI KE WITA (+1 jam dari WIB)
                dt = dt + timedelta(hours=1)

                return f"{dt.day} {bulan[dt.month-1]} {dt.year}, {dt.strftime('%H:%M')} WITA"

            elif isinstance(val, np.integer):
                return int(val)

            elif isinstance(val, np.floating):
                return float(val)

            elif pd.isna(val):
                return ""

            return val
        

        df = df.applymap(clean_value)
        excel_json = df.to_dict(orient="records")

        form_obj = Form.objects.first()

        saved_data = []

        # =========================
        # LOOP DATA
        # =========================
        df.columns = [
            re.sub(r"^\d+\.\s*", "",  # 🔥 hapus "01. ", "2. ", dll di depan
                re.sub(r"\s+", " ", str(col).replace(":", "").strip())
            )
            for col in df.columns
        ]

        name_col = find_column(df, [
            "name", "nama", "nama lengkap"
        ])

        email_col = find_column(df, [
            "email", "email address","alamat email"
        ])

        phone_col = find_column(df, [
            "phone", "no hp", "nohandphone",
            "nomor hp", "nomor telepon", "telepon"
        ])

        location_col = find_column(df, [
            "location", "alamat", "kota", "address"
        ])


        for _, row in df.iterrows():

            name = row[name_col] if name_col else ""
            email = row[email_col] if email_col else ""
            phone = row[phone_col] if phone_col else ""
            location = row[location_col] if location_col else ""

            name = str(name).strip()
            phone = str(phone).strip()

            # hapus .0 dari excel
            phone = re.sub(r"\.0$", "", phone)

            if not any([name, email, phone, location]):
                continue

            # =========================
            # CHECK EXISTING PARTICIPANT
            # =========================
            participant = Participant.objects.filter(
                name__iexact=name,
                phone=phone,
                id_event=event
            ).first()

            # =========================
            # UPDATE JIKA ADA
            # =========================
            if participant:

                participant.email = email
                participant.location = location
                participant.save()

            # =========================
            # CREATE BARU JIKA TIDAK ADA
            # =========================
            else:

                participant = Participant.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    location=location,
                    id_event=event,
                    status_user_id=status_default
                )

            # 🔥 SIMPAN JSON + PARTICIPANT ID
            response_data = {
                "participant_id": participant.id,
                "participant_name": participant.name,
                "participant_email": participant.email,
                "participant_phone": participant.phone,
                 "excel_data": {
                    re.sub(r"^\d+\.\s*", "", key): value
                    for key, value in row.to_dict().items()
                }
            }

            form_response = FormResponse.objects.create(
                form=form_obj,
                data_response=response_data,
                participant=participant
            )

            saved_data.append({
                "participant_id": participant.id,
                "form_response_id": form_response.id
            })

        create_and_send_qremail(request,event_id)

        return JsonResponse({
            "status": "success",
            "message": "Upload berhasil",
            "total_uploaded": len(saved_data),
            "data": saved_data
        })

    except Exception as e:
        return JsonResponse({
            "status": "failed",
            "message": str(e)
        })
    


@csrf_exempt
def download_participant(request):

    if request.method != "GET":
        return JsonResponse({
            "status": "failed",
            "message": "Invalid request"
        })

    event_id = request.GET.get("event_id")

    if not event_id:
        return JsonResponse({
            "status": "failed",
            "message": "Event tidak ditemukan"
        })

    try:
        event = Event.objects.get(id=event_id)

        status_present = StatusParticipant.objects.get(
            status_name__iexact="Present"
        )

        participants = Participant.objects.filter(
            id_event=event,
            status_user_id=status_present
        ).values_list("name", "email", "phone")

        # ✅ DataFrame multi kolom
        df = pd.DataFrame(participants, columns=["Name", "Email", "Phone"])

        # ✅ Tambah kolom status
        df["Status"] = "Check In"

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response['Content-Disposition'] = 'attachment; filename=list_name_participation_lucky_wheel.xlsx'

        df.to_excel(response, index=False, header=True)

        return response

    except StatusParticipant.DoesNotExist:
        return JsonResponse({
            "status": "failed",
            "message": "Status 'Present' tidak ditemukan"
        })

    except Event.DoesNotExist:
        return JsonResponse({
            "status": "failed",
            "message": "Event tidak ditemukan"
        })

    except Exception as e:
        return JsonResponse({
            "status": "failed",
            "message": str(e)
        })

# def filter_video(request):
#     if request.method == 'POST':
#         queryset = PhotoVideoAdsPost.objects.filter(video__isnull = False).order_by('-id')
#         video_filter = PhotoVideoAdsFilter(request.POST, queryset=queryset)

#         page = request.POST.get('page')
#         per_page = request.POST.get('per_page')
#         sort_by = request.POST.get('sort_by')

#         if not sort_by:
#             sort_by = '-id'

#         if not per_page:
#             per_page = 20

#         queryset = video_filter.qs.order_by(sort_by)

#         paginator = Paginator(queryset,per_page=per_page)

#         try:
#             list_video = paginator.page(page)
#         except PageNotAnInteger:
#             list_video = paginator.page(1)
#         except EmptyPage:
#             list_video = paginator.page(paginator.num_pages)

#         context = {'list_video':list_video,}

#         template = 'template/views/view_video_list.html'
#         html = render_to_string(template_name=template, context=context, request = request, using=None)
#         return HttpResponse(html)

# def current_video(request):
#     if request.method == 'POST':
#         user = request.user
#         id_video = request.POST.get('id_video')

#         selected_video = PhotoVideoAdsPost.objects.filter(id = id_video).first()

#         html = mark_safe(''' 
#                         <video width="350" height="auto" controls autoplay>
#                             <source src="%s" type="audio/mp4" id="current_video" />
#                         </video>
#                         '''% (selected_video.video.url))
        
#         return HttpResponse(html)

# def filter_photo(request):
#     if request.method == 'POST':
#         queryset = PhotoVideoAdsPost.objects.filter(photo__isnull = False).order_by('-id')
#         photo_filter = PhotoVideoAdsFilter(request.POST, queryset=queryset)

#         page = request.POST.get('page')
#         per_page = request.POST.get('per_page')
#         sort_by = request.POST.get('sort_by')

#         if not sort_by:
#             sort_by = '-id'

#         if not per_page:
#             per_page = 20

#         queryset = photo_filter.qs.order_by(sort_by)

#         paginator = Paginator(queryset,per_page=per_page)

#         try:
#             list_photo = paginator.page(page)
#         except PageNotAnInteger:
#             list_photo = paginator.page(1)
#         except EmptyPage:
#             list_photo = paginator.page(paginator.num_pages)

#         context = {'list_photo':list_photo,}

#         template = 'template/views/view_photo_list.html'
#         html = render_to_string(template_name=template, context=context, request = request, using=None)
#         return HttpResponse(html)

# def current_photo(request):
#     if request.method == 'POST':
#         id_photo = request.POST.get('id_photo')

#         selected_photo = PhotoVideoAdsPost.objects.filter(id = id_photo).first()

#         html = mark_safe(''' <img src="%s" alt="" id="current_photo" style="max-width:500px; height:auto;">
#                         '''% (selected_photo.photo.url))
        
#         return HttpResponse(html)