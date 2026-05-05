from django.contrib.auth import password_validation, authenticate, login as user_login, logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator

from django.core import validators,serializers as serial
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.forms import modelformset_factory, formset_factory

from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch
from django.db.models.functions import Coalesce, Concat
from django.db import IntegrityError as connection
from django.db import transaction as trans_connect

from pathlib import Path
import json
import random
from django.conf import settings
import os
import re
import hashlib
import string  
import secrets 
from itertools import chain 

from datetime import datetime, timedelta
from PIL import Image

from django.contrib.postgres.search import SearchVector
from decimal import Decimal
from django.template.loader import render_to_string
from django.template import RequestContext

#EMAIL VERIFICATION AND TOKEN
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.safestring import SafeString

#Test Exception
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from rest_framework.authtoken.models import Token
from django.db.models.functions import Replace
from django.db.models import Value

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.decorators import *
from gallery.models import *
from authentication.models import *
from event.models import *
from event.serializers import *
from participant.models import *
from participant.serializers import *
from portfolio.models import *
from portfolio.serializers import *
from utils.utils import *
from authentication.forms import *

import base64

#Set Logg
import logging
logger = logging.getLogger(__file__)

from django.contrib.auth import get_user_model
UserModel = get_user_model()

@api_view(['GET'])
def list_events(request):
    if request.method == 'GET':
        try:
            now = datetime.now()
            end_time = now + timedelta(hours=2)
            start_date = now - timedelta(days=2)

            events = Event.objects.filter(date__gte = start_date)
            on_going = events.filter(date__lte=now.date(), time__lte=now.time()).filter(date__lte = end_time.date(), time__lte = end_time.time()).first()
            on_comming = events.filter(date__gte = now.date(), time__gte = now.time()).order_by("date", "time")
            if on_going:
                on_comming = on_comming.exclude(id = on_going.id)

            on_going_serializer = ListofEventSerializer(on_going, many=False)
            on_comming_serializer = ListofEventSerializer(on_comming, many=True)
            status_code = status.HTTP_200_OK
            message = "Ok"
            context = { "on_going": on_going_serializer.data,
                        "on_comming": on_comming_serializer.data,
                        "metadata": metadata_api(status_code,message)}
            return Response(context,status=status_code)
        
        except Exception as err:
            message = "Server Error, please contact the administration."
            logger.info("Error Login "+str(err))
            status_code = status.HTTP_201_CREATED
            context = { "event": "",
                        "metadata": metadata_api(status_code,message)}
            return Response(context,status=status_code)

    else:
        error_method()

@api_view(['GET'])
def event_detail(request):
    if request.method == 'GET':
        uuid = request.headers.get("x-eventuuid")
        # uuid = 'cde2f177-275d-4c40-a0b3-8b9839551046'
        try:
            event = Event.objects.filter(unique_name = uuid).first()
            participants = Participant.objects.filter(id_event = event)
            
            event = ListofEventSerializer(event, many=False)
            participants = ListofParticipantsSerializer(participants, many=True)

            status_code = status.HTTP_200_OK
            message = "Ok"
            context = { "event": event.data,
                        "participants": participants.data,
                        "metadata": metadata_api(status_code,message)}
            return Response(context,status=status_code)
        except Exception as err:
            message = "Server Error, please contact the administration."
            logger.info("Error Login "+str(err))
            status_code = status.HTTP_201_CREATED
            context = { "event": "",
                        "participants": "",
                        "metadata": metadata_api(status_code,message)}
            return Response(context,status=status_code)
    else:
        error_method()

@api_view(['POST'])
def check_participant(request):
    if request.method == 'POST':
        try:
            data = request.data
            eventUuid = data['eventUuid']
            participantUuid = data['participantUuid']
            
            now = datetime.now()
            event = Event.objects.filter(unique_name = eventUuid, date__gte = now).first()
            if event:
                participant = Participant.objects.filter(unique_user = participantUuid).exclude(status_user_id = 4).first()
                if participant:
                    if participant.id_event.id == event.id:
                        if participant.status_user_id.id != 1:
                            status_participant = StatusParticipant.objects.filter(status_name = "Present").first()
                            participant.status_user_id = status_participant
                            participant.save()
                        message = "Ok"
                        status_code = status.HTTP_200_OK
                        context = {"message":message}
                    else:
                        message = "The participant is not found in this event."
                        status_code = status.HTTP_201_CREATED
                        context = {"message":message}
                else:
                    message = "Participant not found"
                    status_code = status.HTTP_201_CREATED
                    context = {"message":message}
            else:
                message = "Event not found or has completed."
                status_code = status.HTTP_201_CREATED
                context = {"message":message}
                
            return Response(context,status=status_code)

        except Exception as err:
            message = "Server Error, please contact the administration."
            logger.info("Error Login "+str(err))
            status_code = status.HTTP_201_CREATED
            context = {metadata_api(status_code,message)}
            return Response(context,status=status_code)