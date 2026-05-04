from re import U
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from authentication.models import UserData
from .models import *

class ListofEventSerializer(serializers.ModelSerializer):
    poster = serializers.ReadOnlyField()
    class Meta:
        model = Event
        exclude = ['id']