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

@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        try:
            data = request.data
            username = data['username']
            password = data['password']
            token = None       

            if username is not None and password:
                username_exist = UserData.objects.filter(Q(username=username) | Q(email=username)).first()
                if username_exist:
                    if username_exist.is_validate:
                        if username_exist.is_active:
                            user_cache = authenticate(request, username=username_exist.username, password=password)
                            if user_cache is None:
                                message = "Username / password tidak sesuai"
                                status_code = status.HTTP_201_CREATED
                            else:
                                if user_cache.is_admin:
                                    status_code = status.HTTP_201_CREATED
                                    message = "Anda tidak dapat login melalui halaman ini"
                                else:
                                    username = username_exist.username
                                    token = Token.objects.get_or_create(user=username_exist)[0].key
                                    message = "Berhasil login"
                                    status_code = status.HTTP_200_OK
                        else:
                            status_code = status.HTTP_201_CREATED
                            message = "Akun anda tidak aktif"
                    else:
                        status_code = status.HTTP_201_CREATED
                        message = "Akun anda belum divalidasi, validasi melalui email"
                else:
                    message = "Tidak dapat menemukan username / email"
                    status_code = status.HTTP_201_CREATED
                context = {"username": username,
                        "token": token,
                        "metadata": metadata_api(status_code,message)}
                return Response(context,status=status_code)
            else:
                message = "Harap isi username dan password dengan benar."
                status_code = status.HTTP_201_CREATED
                context = {"username": username,
                        "token": token,
                        "metadata": metadata_api(status_code,message)}
                return Response(context,status=status_code)
        except Exception as err:
            message = "Harap isi username dan password dengan benar."
            logger.info("Error Login "+str(err))
            status_code = status.HTTP_201_CREATED
            context = { "username": None,
                        "token": None,
                        "metadata": metadata_api(status_code,message)}
            return Response(context,status=status_code)

    else:
        error_method()