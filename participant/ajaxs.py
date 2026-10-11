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

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

def ajax_update_participant_status(request):
    if request.method == 'POST':
        try:
            new_status = request.POST.get('new_status', None)
            id = request.POST.get('id', None)
            id = decoding_id(id)

            participant = Participant.objects.filter(id = id).first()
            if participant:
                q_status = StatusParticipant.objects.filter(status_name = new_status).first()
                participant.status_user_id = q_status
                participant.save()

                message = "Ok"
            else:
                message = "Participant not found"
                
            context = {
                "status":message}
                
            return JsonResponse(context)

        except Exception as err:
            message = "Server Error, please contact the administration."
            logger.info("Error Login "+str(err))
            context = {
                "status":message}
            return JsonResponse(context)
    else:
        error_method()