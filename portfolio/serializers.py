from rest_framework.serializers import ModelSerializer
from portfolio.models import *

class ServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'