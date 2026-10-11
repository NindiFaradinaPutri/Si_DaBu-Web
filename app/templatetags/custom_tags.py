from datetime import datetime
from django import template
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.conf import settings
from gallery.models import *
from profile.models import *
from portfolio.models import *
# from information.models import *

register = template.Library()

@register.filter()
def gallery_table(gallery):
    if gallery.video:
        video = format_html('{}{}',settings.MEDIA_URL,gallery.video)
        return format_html("<video controls preload='none' class='w-100px'> <source src='{}' type='video/mp4'></video>",video,gallery.informasi)
    elif gallery.foto:
        img = format_html('{}{}',settings.MEDIA_URL,gallery.foto)
        return format_html("<img src='{}' alt='{}' class='w-100px'/>", img, gallery.informasi)
    elif gallery.link:
        link = gallery.link
        img = format_html('{}{}/maxresdefault.jpg','https://i.ytimg.com/vi/',link.split("v=")[1][:11])
        return format_html("<img src='{}' alt='{}' class='w-100px'/>", img, gallery.informasi)
    else:
        return format_html("")

@register.filter()
def photo_link(link):
    img = format_html('{}{}/maxresdefault.jpg','https://i.ytimg.com/vi/',link.split("v=")[1][:11])
    return format_html("<img src='{}' alt='' class='img-fluid border-radius-0 img-gallery'/>", img)

@register.filter()
def video_link(link):
    linkvid = format_html('{}{}','https://www.youtube.com/embed/',link.split("v=")[1][:11])
    return format_html("<iframe src='{}'></iframe>", linkvid)

@register.filter()
def contact_silatama(type):
    contact = Contact.objects.filter(id=1).first()
    if contact:
        if type == 'address':
            if contact.address:
                return str(contact.address)
            else:
                return '-'
        if type == 'phone':
            if contact.phone:
                #return str(contact.phone)
                return f'{contact.phone[:3]} {contact.phone[3:6]} {contact.phone[6:10]} {contact.phone[10:]}'
            else:
                return '-'
        if type == 'whatsapp':
            if contact.whatsapp:
                return str(contact.whatsapp)
            else:
                return '-'
        if type == 'email':
            if contact.email:
                return str(contact.email)
            else:
                return '-'
        if type == 'working':
            if contact.working_hour:
                return str(contact.working_hour)
            else:
                return '-'
        if type == 'sla':
            if contact.sla:
                return format_html(contact.sla)
            else:
                return '-'
    else:
        return '-'

@register.filter()
def count_gallery(type):
    if type == 'all':
        gallery = Gallery.objects.all()
        if gallery:
            return str(gallery.count())
        else:
            return str(0)
    elif type == 'photo':
        gallery = Gallery.objects.exclude(foto = '')
        if gallery:
            return str(gallery.count())
        else:
            return str(0)
    elif type == 'video':
        gallery = Gallery.objects.exclude(video = '')
        if gallery:
            return str(gallery.count())
        else:
            return str(0)
    elif type == 'link':
        gallery = Gallery.objects.filter(link__isnull=False)
        if gallery:
            return str(gallery.count())
        else:
            return str(0)

@register.filter()
def custom_header(type):
    contact = Contact.objects.filter(id = 1).first()
    if type == 'email':       
        if contact and contact.email:
            return contact.email
        else:
            return None
    elif type == 'phone':
        if contact and contact.phone:
            #return contact.phone
            #phone_array = [str(contact.phone)[i:i+4] for i in range(0, len(contact.phone),4)]
            #return " ".join(phone_array)
            return f'{contact.phone[:3]} {contact.phone[3:6]} {contact.phone[6:10]} {contact.phone[10:]}'
        else:
            return None
    elif type == 'address':
        if contact and contact.address:
            return contact.address
        else:
            return None
    elif type == 'working_hour':
        if contact and contact.working_hour:
            return contact.working_hour
        else:
            return None
    elif type == 'whatsapp':
        if contact and contact.whatsapp:
            return contact.whatsapp
        else:
            return None
    elif type == 'instagram':
        if contact and contact.instagram:
            return contact.instagram
        else:
            return 'http://www.instagram.com/'
    elif type == 'tiktok':
        if contact and contact.tiktok:
            return contact.tiktok
        else:
            return 'https://www.tiktok.com/'
    elif type == 'facebook':
        if contact and contact.facebook:
            return contact.facebook
        else:
            return None
    elif type == 'youtube':
        if contact and contact.youtube:
            return contact.youtube
        else:
            return None
    elif type == 'twitter':
        if contact and contact.twitter:
            return contact.twitter
        else:
            return None
    elif type == 'linkedin':
        if contact and contact.linkedin:
            return contact.linkedin
        else:
            return 'http://www.linkedin.com/'
       
@register.filter()
def get_year(year):
    if str(year) == str(datetime.today().year):
        return 'show'
    else:
        return ''

@register.filter()
def custom_footer(type):
    if type == 'brief':
        query = Profile.objects.filter(id = 1).first()
        if query:
            return query.brief
        else:
            return ''
    elif type == 'visi':
        query = Profile.objects.filter(id = 1).first()
        if query:
            return query.visi
        else:
            return ''
    elif type == 'kegiatan':
        kegiatan = KegiatanMasjid.objects.all().order_by('id')
        if kegiatan:
            return kegiatan
        else:
            dummy = {
                'Kegiatan 1', 'Kegiatan 2', 'Kegiatan 3', 'Kegiatan 4', 'Kegiatan 5', 
                }
            return dummy

@register.filter()
def porto_photo(id):
    porto = PortfolioAttachment.objects.filter(portfolio = id ,is_main = True).first()
    if porto:
        return porto.file
    else:
        porto_emr = PortfolioAttachment.objects.filter(portfolio = id).first()
        return porto_emr.file

@register.filter()
def porto_word(word):
    x = len(word.split())
    if x < 3:
        return True
    else:
        return False

@register.filter()
def int_format(value):
    return int(str(value).replace('.',''))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def trim(value):
    if isinstance(value, str):
        return value.strip()
    return value

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()