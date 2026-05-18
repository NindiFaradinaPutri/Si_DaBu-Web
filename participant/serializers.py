from re import U
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from authentication.models import UserData
from .models import *

class ListofParticipantsSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()
    class Meta:
        model = Participant
        exclude = ['id', 'id_event', 'status_user_id']

class StatusListSerializer(serializers.ModelSerializer):
    encrypt_id = serializers.ReadOnlyField()
    class Meta:
        model = StatusParticipant
        exclude = ['id']