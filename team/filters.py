import django_filters as filter
from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch

from service.models import *
from banner.models import *

class PhotoVideoAdsFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = PhotoVideoAdsPost
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        query = queryset.first()
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            if query.video:
                result = PhotoVideoAdsPost.objects.filter(Q(title__icontains = word)).filter(video__isnull = False).order_by('-id')
                queryset = result
            else:
                result = PhotoVideoAdsPost.objects.filter(Q(title__icontains = word)).filter(photo__isnull = False).order_by('-id')
                queryset = result

        return queryset