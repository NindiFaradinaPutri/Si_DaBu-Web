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

from service.models import *

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

#START SERVICE TABLES
class ServiceTable(tables.Table):
    no = tables.Column(empty_values=(),attrs={"td":{"width":"10%"}})
    service_code = tables.Column(verbose_name="Kode Jasa", default='', order_by='service_code',attrs={"td":{"width":"15%"}})
    service_name = tables.Column(verbose_name="Nama Jasa", default='', order_by='service_name',attrs={"td":{"width":"15%"}})
    service_brief = ShortInformation(verbose_name='Ringkasan', orderable=False, attrs={"td":{"width":"20%"}})
    service_description = ShortInformation(verbose_name='Deskripsi', orderable=False, attrs={"td":{"width":"20%"}})
    photo = ImageColumn(verbose_name='Foto', orderable=False, attrs={"td":{"width":"10%"}})
    is_active = tables.Column(verbose_name="Aktif",order_by='is_active',empty_values=(),attrs={"td":{"width":"10%"}})
    action = tables.Column(verbose_name="Aksi",orderable=False,empty_values=(),attrs={"td":{"width":"10%"}})

    class Meta:
        model = Service
        exclude = ('id','creation_date','update_date')
        sequence = ('no','service_code','service_name','service_brief','service_description','is_active','photo','action')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.empty_text = 'Tidak ditemukan data Jasa'

    def render_no(self):
        if self.page:
            counter = next(self.counter) + self.page.start_index()
        else:
            counter = next(self.counter)
        return "%d" % counter

    def render_action(self, record):
        edit_url = reverse("service_update", kwargs={'status':'edit','id':record.pk})
        delete_url = reverse("service_update",kwargs={'status':'delete','id':record.pk})
        return mark_safe('''<a href="%s" class="btn btn-sm btn-block btn-warning" id="id_edit">
                                <i class="bx bx-edit text-blue"></i>ubah
                            </a>
                         <a href="#" class="btn btn-sm btn-block btn-danger" data-href="%s" data-name="%s" data-toggle="modal" data-target="#deleteConfirmationModals">
                                <i class="bx bx-trash text-red"></i>hapus
                        </a>'''% (edit_url, delete_url, record.service_name ))
#END SERVICE TABLES

class UserServiceTable(tables.Table):
    no = tables.Column(empty_values=(),attrs={"td":{"width":"10%"}})
    service = tables.Column(verbose_name="Jasa", default='', order_by='service__service_code',attrs={"td":{"width":"15%"}})
    talent = tables.Column(verbose_name="Talent", default='', order_by='talent',attrs={"td":{"width":"15%"}})
    user_brief = ShortInformation(verbose_name='Ringkasan', orderable=False, attrs={"td":{"width":"20%"}})
    user_information = ShortInformation(verbose_name='Deskripsi', orderable=False, attrs={"td":{"width":"20%"}})
    experience = tables.Column(verbose_name="Pengalaman", orderable=False,empty_values=(),attrs={"td":{"width":"15%"}})
    action = tables.Column(verbose_name="Aksi",orderable=False,empty_values=(),attrs={"td":{"width":"10%"}})

    class Meta:
        model = UserService
        exclude = ('id','creation_date','update_date','user_exp_claimed','exp_claimed_matric')
        sequence = ('no','service','talent','user_brief','user_information','experience','action')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count()
        self.empty_text = 'Tidak ditemukan data Jasa'

    def render_no(self):
        if self.page:
            counter = next(self.counter) + self.page.start_index()
        else:
            counter = next(self.counter)
        return "%d" % counter

    def render_experience(self, record):
        experience = str(record.user_exp_claimed) +' '+str(record.exp_claimed_matric)
        if experience:
            return experience
        else:
            return "Belum ada pengalaman"

    def render_action(self, record):
        edit_url = reverse("user_service_update", kwargs={'status':'edit','service':'service','id':record.pk})
        delete_url = reverse("user_service_update",kwargs={'status':'delete','service':'service','id':record.pk})
        return mark_safe('''<a href="%s" class="btn btn-sm btn-block btn-warning" id="id_edit">
                                <i class="bx bx-edit text-blue"></i>ubah
                            </a>
                         <a href="#" class="btn btn-sm btn-block btn-danger" data-href="%s" data-name="%s" data-toggle="modal" data-target="#deleteConfirmationModals">
                                <i class="bx bx-trash text-red"></i>hapus
                        </a>'''% (edit_url, delete_url, record.service.service_name ))

