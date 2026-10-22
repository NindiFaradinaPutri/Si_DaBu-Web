from utils.utils import *
from app.decorators import *
from django.views.decorators.csrf import csrf_exempt
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

import requests

from information.models import *
from information.forms import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#Set Loggin
import logging
logger = logging.getLogger(__file__)

from django.utils import timezone
current_tzinfo = timezone.get_current_timezone()

import random

def add_rekening_detail(request):
	if request.method == 'POST':
		no_rek = request.POST.get('no_rek','')
		rekening = RekeningMasjid.objects.filter(no_rek = no_rek).first()
		rekening_attachment = RekeningMasjidAttachment.objects.filter(rekening=rekening).first()

		rekening_html_start = '<table class="table mb-0">'
		rekening_html_end = '</table>'
		rekening_detail = ''
		
		if rekening_attachment:
			if no_rek:
				rekening_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">No Rek:</label></td>'
														'<td>%s</td>'
													'</tr>'%(no_rek))

			if rekening_attachment.photo:
				rekening_html_start  += mark_safe(	'<tr>'
														'<td><label class="mb-0">Foto:</label></td>'
														'<td> <img src="/media/%s" class="img-fluid border-radius-0 img-gallery" alt="">'
														'</td>'
													'</tr>'%(rekening_attachment.photo))

			if rekening_attachment.attachment:
				rekening_html_start  += mark_safe(	'<tr>'
														'<td><label class="mb-0">Lampiran:</label></td>'
														'<td><a href="/media/%s" download>%s</a>'
														'</td>'
													'</tr>'%(rekening_attachment.attachment, rekening_attachment.name))

			rekening_detail = rekening_html_start + rekening_html_end
			
		else:
			rekening_detail = ''
		
		return HttpResponse(rekening_detail)

def add_kutipan_detail(request):
	if request.method == 'POST':
		title = request.POST.get('title','')
		kutipan = KutipanPilihan.objects.filter(title = title).first()

		kutipan_html_start = '<table class="table mb-0">'
		kutipan_html_end = '</table>'
		kutipan_detail = ''
		
		if kutipan:
			if kutipan.quotes:
				kutipan_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Pesan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(kutipan.quotes))

			if kutipan.notes:
				kutipan_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Catatan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(kutipan.notes))
			

			kutipan_detail = kutipan_html_start + kutipan_html_end
			
		else:
			kutipan_detail = ''
		
		return HttpResponse(kutipan_detail)

def add_khutbah_detail(request):
	if request.method == 'POST':
		title = request.POST.get('title','')
		khutbah = KhutbahJumat.objects.filter(title = title).first()

		khutbah_html_start = '<table class="table mb-0">'
		khutbah_html_end = '</table>'
		khutbah_detail = ''
		
		if khutbah:
			if khutbah.brief:
				khutbah_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">ringkasan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(khutbah.brief))

			if khutbah.naration:
				khutbah_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Pesan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(khutbah.naration))

			if khutbah.quotes:
				khutbah_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Catatan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(khutbah.quotes))
			

			khutbah_detail = khutbah_html_start + khutbah_html_end	
		else:
			khutbah_detail  = ''
		
		return HttpResponse(khutbah_detail)

def add_kegiatan_detail(request):
	if request.method == 'POST':
		title = request.POST.get('title','')
		kegiatan = KegiatanMasjid.objects.filter(title = title).first()

		kegiatan_html_start = '<table class="table mb-0">'
		kegiatan_html_end = '</table>'
		kegiatan_detail = ''
		
		if kegiatan:
			if kegiatan.brief:
				kegiatan_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">ringkasan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(kegiatan.brief))

			if kegiatan.naration:
				kegiatan_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Pesan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(kegiatan.naration))

			if kegiatan.quotes:
				kegiatan_html_start  += mark_safe(	'<tr class="b-top-0">'
														'<td><label class="mb-0">Catatan:</label></td>'
														'<td>%s</td>'
													'</tr>'%(kegiatan.quotes))
			

			kegiatan_detail = kegiatan_html_start + kegiatan_html_end	
		else:
			kegiatan_detail  = ''
		
		return HttpResponse(kegiatan_detail)

def view_kegiatan(request):
    if request.method == 'POST':
        data_id = request.POST.get('data_id',None)

        data_id = decoding_id(data_id)

        kegiatan = KegiatanMasjid.objects.get(id = data_id)

        context = {
                'kegiatan':kegiatan,
                }
        template = 'views/kegiatan.html'
        html = render_to_string(template_name=template, context=context, request = request, using=None)
        return HttpResponse(html)
	
@csrf_exempt
def synch_jadwal_sholat(request):
	if request.method == 'POST':
		bpn_code = "2308"
		today = datetime.now().astimezone(current_tzinfo).date().strftime(('%Y/%m/%d'))
		url_sholat = "https://api.myquran.com/v1/sholat/jadwal/"+bpn_code+'/'+today
		headers = {"accept": "application/json"}
		response = requests.get(url_sholat, headers=headers)
		jadwal_sholat_raw = response.json()
		jadwal_sholat_clean = jadwal_sholat_raw.get('data').get('jadwal')
    
		jadwal_sholat = {}
		jadwal_sholat['imsak'] = str(jadwal_sholat_clean.get('imsak'))
		jadwal_sholat['subuh'] = str(jadwal_sholat_clean.get('subuh'))
		jadwal_sholat['dzuhur'] = str(jadwal_sholat_clean.get('dzuhur'))
		jadwal_sholat['ashar'] = str(jadwal_sholat_clean.get('ashar'))
		jadwal_sholat['maghrib'] = str(jadwal_sholat_clean.get('maghrib'))
		jadwal_sholat['isya'] = str(jadwal_sholat_clean.get('isya'))

		data = {
			'jadwal_sholat': json.dumps(jadwal_sholat),
		}

		return JsonResponse(data)
	
# @csrf_exempt
# def get_random_slide(request):
#     try:
#         res = requests.get(
#             "https://api.myquran.com/v3/quran/random",
#             timeout=5
#         )

#         if res.status_code != 200:
#             return JsonResponse({"type": "error", "msg": "API gagal"})

#         json_data = res.json()

#         if not json_data.get("status"):
#             return JsonResponse({"type": "error", "msg": "Data kosong"})

#         data = json_data["data"]

#         slide = {
#             "type": "quran",
#             "title": data["surah"]["name_latin"],   
#             "subtitle": data["surah"]["name"], 
#             "subtitle": f"No. {data.get('id','')} : {data.get('grade', '')}",     
#             "description": data["translation"],     
#             "arabic": data["arab"]                
#         }

#     except Exception as e:
#         print("ERROR:", e)
#         slide = {
#             "type": "error",
#             "msg": str(e)
#         }

#     return JsonResponse(slide)


def get_random_slide(request):
    MAX_LENGTH = 600  # batas maksimal karakter
    MIN_LENGTH = 20
    MAX_TRY = 5       # biar tidak infinite loop

    for _ in range(MAX_TRY):
        slide_type = random.choice(["quran", "hadith"])

        try:
            # =========================
            # QURAN
            # =========================
            if slide_type == "quran":
                res = requests.get(
                    "https://api.myquran.com/v3/quran/random",
                    headers={"Accept": "application/json"},
                    timeout=5
                ).json()

                data = res.get("data", {})
                surah = data.get("surah", {})
                text = data.get("translation", "")

                # 🔥 FILTER PANJANG
                if len(text) > MAX_LENGTH:
                    continue  # skip, ambil data lain
                if len(text) < MIN_LENGTH:
                    continue  # skip, ambil data lain

                return JsonResponse({
                    "type": "quran",
                    "title": surah.get("revelation"),
                    "subtitle": f"QS {surah.get('name', '')} : {data.get('ayah_number', '')}",
                    "description": text,
                    "arabic": data.get("arab", "")
                })

            # =========================
            # HADITH
            # =========================
            else:
                res = requests.get(
                    "https://api.myquran.com/v3/hadis/enc/random",
                    headers={"Accept": "application/json"},
                    timeout=5
                ).json()

                data = res.get("data", {})
                text = data.get("text", {}).get("id", "")

                # 🔥 FILTER PANJANG
                if len(text) > MAX_LENGTH:
                    continue  # skip
                if len(text) < MIN_LENGTH:
                    continue  # skip, ambil data lain
                
                return JsonResponse({
                    "type": "hadith",
                    "title": data.get("takhrij", "Hadist"),
                    "subtitle": f"No. {data.get('id','')} : {data.get('grade', '')}",
                    "description": text,
                    "arabic": data.get("text", {}).get("ar", "")
                })

        except Exception as e:
            continue

    # ❗ fallback kalau semua gagal
    return JsonResponse({
        "type": "error",
        "message": "Tidak ada data yang sesuai"
    })