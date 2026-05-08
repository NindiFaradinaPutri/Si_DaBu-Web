"""
Definition of views.
"""

from django.contrib.auth import password_validation, authenticate, login as user_login, logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib import messages



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
from django.db import IntegrityError, transaction, connection

from pathlib import Path
import json
import random
from django.conf import settings
import os
import re
import hashlib
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
from portfolio.models import *
from portfolio.serializers import *
from utils.utils import *

#Set Logg
import logging
logger = logging.getLogger(__file__)

#Set Masking
from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

@api_view(['GET'])
def getService(request):
    service = Service.objects.all()
    serializer = ServiceSerializer(service, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getOneService(request, pk):
    service = Service.objects.filter(id=pk).first()
    serializer = ServiceSerializer(service, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def createService(request):
    data = request.data

    service = Service.objects.create(
        name=data['name'], brief=data['brief'], description=data['description'],is_active=True
    )
    serializer = ServiceSerializer(service, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
def updateService(request, pk):
    data = request.data

    service = Service.objects.filter(id=pk).first()
    serializer = ServiceSerializer(service, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteService(request, pk):
    service = Service.objects.filter(id=pk).first()
    service.delete()
    return Response('Service successfully deleted')