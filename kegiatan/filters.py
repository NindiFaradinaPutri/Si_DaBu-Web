from audioop import add
import django_filters as filter
from django.db.models import Q, CharField, Value, Sum, F, Case, When, Exists, Prefetch

from kegiatan.models import *


class KegiatanFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = Kegiatan
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        query = queryset
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = Kegiatan.objects.filter(Q(informasi__icontains = word))
            queryset = result

        return queryset
    
#kegiatan transaksi

class COAGroupFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = ChartOfAccountsGroup
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = ChartOfAccountsGroup.objects.filter(Q(group_name__icontains = word))
            queryset = queryset.union(result)

        return queryset
    
class COAFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')

    class Meta:
        model = ChartOfAccounts
        fields = ['keyword']

    def search_keyword(self, queryset, name, value):
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = ChartOfAccounts.objects.filter(Q(account_name__icontains = word) | Q(code__icontains = word) | Q(information__icontains = word) | Q(group__group_name__icontains = word) | Q(account_type__icontains = word))
            queryset = queryset.union(result)

        return queryset

class GeneralLedgerFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')
    date = filter.DateFilter(field_name='date', lookup_expr='exact', input_formats=settings.DATE_INPUT_FORMATS, label="Tanggal Transaksi")

    class Meta:
        model = KegiatanAkuntasi
        fields = ['keyword','date']

    def search_keyword(self, queryset, name, value):
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = KegiatanAkuntasi.objects.filter(Q(transaction__icontains = word))
            queryset = queryset.union(result)

        return queryset