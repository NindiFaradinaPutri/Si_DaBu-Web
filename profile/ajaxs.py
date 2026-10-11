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

#Set Loggin
import logging
logger = logging.getLogger(__file__)