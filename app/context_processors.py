from django.conf import settings
from news.models import *

def google_map_key(request):
    return {'google_map_key':settings.RSAD_GOOGLE_MAP_KEY}

def posts(request):
    return {
        'all_posts': News.objects.order_by('post_date'),
    }