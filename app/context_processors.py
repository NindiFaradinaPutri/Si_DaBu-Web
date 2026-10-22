from django.conf import settings
<<<<<<< HEAD
# from news.models import *
=======
from news.models import *
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609

def google_map_key(request):
    return {'google_map_key':settings.RSAD_GOOGLE_MAP_KEY}

def posts(request):
    return {
<<<<<<< HEAD
        'all_posts': '',
=======
        'all_posts': News.objects.order_by('post_date'),
>>>>>>> e4194ca216db50688a23ff8065f35fe3865ef609
    }