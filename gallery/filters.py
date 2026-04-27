import django_filters as filter
from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch

from gallery.models import *

class GalleryFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = Gallery
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        query = queryset
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = Gallery.objects.filter(Q(informasi__icontains = word))
            queryset = result

        return queryset