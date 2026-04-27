"""
Definition of forms.
"""

from django.db import models

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.conf import settings
import django_tables2 as tables 
from django_tables2.utils import A, Accessor, AttributeDict
import itertools

import django_filters as filter 

from kegiatan.models import *

class ImageColumn(tables.Column):
    def render(self, value):
        img = format_html('{}{}',settings.MEDIA_URL,value)
        return format_html("<img src='{}' alt='{}' class='w-100'/>", img, value)

class NumberColumn(tables.Column):
    def render(self, value):
        return int(value)

class FileColumn(tables.Column):
    def render(self, value):
        file = format_html('{}{}',settings.MEDIA_URL, value)
        return format_html("<a href='{}' target='_blank' class='icon'><i class='fas fa-file'></i></a>",file)

class ShortInformation(tables.Column):
    def render(self, value):
        if len(value) > 50:
            content = mark_safe(value[0:49])
            return "%s..." % content
        return str(value)

class ShortHTMLInformation(tables.Column):
    def render(self, value):
        if len(value) > 200:
            content = mark_safe('%s...%s'%(value[0:200],'"'))
            return "%s..." % content
        return str(value)
    
    
class class1(object):
    """description of class"""