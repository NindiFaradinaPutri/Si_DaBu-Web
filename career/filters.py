import django_filters as filter
from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch

from career.models import *