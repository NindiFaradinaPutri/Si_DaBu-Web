import django_filters as filter
from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch

from authentication.models import *

class UserFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = UserProfile
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        group = queryset.first().user.is_admin
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            if group == True:
                result = UserProfile.objects.filter(Q(user__username__icontains = word) | Q(first_name__icontains = word) | Q(last_name__icontains = word)).filter(user__groups__name = 'Admin')
            else:
                result = UserProfile.objects.filter(Q(user__username__icontains = word) | Q(first_name__icontains = word) | Q(last_name__icontains = word)).filter(user__groups__name = 'User')
            queryset = result

        return queryset
