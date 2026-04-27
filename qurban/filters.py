from audioop import add
import django_filters as filter

from qurban.models import *
  
class QurbanTypeFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')
    
    class Meta:
        model = QurbanType
        fields = ['keyword']
        
    def search_keyword(self, queryset, name, value):
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = QurbanType.objects.filter(Q(qurban_type__icontains = word) | Q(information__icontains = word))
            queryset = queryset.union(result)

        return queryset
    
class QurbanTypeFilter(filter.FilterSet):
    keyword = filter.CharFilter(lookup_expr='icontains',label="Kata Kunci",method='search_keyword')
    
    class Meta:
        model = QurbanType
        fields = ['keyword']
        
    def search_keyword(self, queryset, name, value):
        keyword = value.split(" ")

        for index,word in enumerate(keyword):
            result = QurbanType.objects.filter(Q(qurban_type__icontains = word) | Q(information__icontains = word))
            queryset = queryset.union(result)

        return queryset
    