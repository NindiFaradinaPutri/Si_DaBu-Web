import email
import os
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from event.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)

#START PARTICIPANT MODEL

class StatusParticipant(models.Model):
    status_name = models.CharField(max_length=100)
    information = models.CharField(max_length=225)

    class Meta:
        db_table = 'status_participant'

    def __str__(self):
        return self.status_name

class Participant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    location = models.CharField(max_length=150, null=True, blank=True)
    status_user_id = models.ForeignKey(StatusParticipant, on_delete=models.SET_NULL,null=True, blank=True)
    unique_user = models.UUIDField(default=uuid4, editable=False, unique=True)
    id_event = models.ForeignKey(Event,on_delete=models.CASCADE, null=False, blank=False)
    qr_code = models.ImageField(upload_to=path_qr_code, null=True, blank=True)
    is_winner = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True, blank=False)
    update_date = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        db_table = 'participant'

    def __str__(self):
        return self.name
    
    @property
    def encrypt_id(self):
        return hashid.encode(self.pk)

    @property
    def upload_photo_to(self):
        return 'qr_code/'

    @property
    def photo_rename(self):
        try:
            newname = ''.join(self.unique_user.replace(" ","")).upper().join(self.id_event.unique_name.replace(" ","")).upper()
            name = '{}{}'.format('br',newname)
        except Exception as err:
            name = ''
        return name
    
    @property
    def status(self):
        status = StatusParticipant.objects.filter(id = self.status_user_id.id).first()
        if status:
            return status.status_name
        else:
            return ""
        
    @property
    def photoname(self, *args, **kwargs):
        return self.qr_code.name.split('/')[-1]

    def save(self, *args, **kwargs):
        try:
            if self.pk:
                old = Participant.objects.get(pk=self.pk)

                if old.qr_code and old.qr_code != self.qr_code:
                    old.qr_code.delete(save=False)

        except Participant.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            items = Participant.objects.filter(id=self.id)
            if items:
                for item in items:
                    item.qr_code.delete(save=False)
        except Exception as e:
            pass
        super(Participant, self).delete(*args, **kwargs)

#END OF PARTICIPANT MODEL


# =========================================================
# DOORPRIZE
# =========================================================

class Doorprize(models.Model):

    STATUS_CHOICES = (
        ("ACTIVE", "ACTIVE"),
        ("DONE", "DONE"),
    )

    id_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="doorprizes"
    )

    prize_name = models.CharField(max_length=255)

    qty = models.PositiveIntegerField(default=1)

    winner = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_prizes"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    creation_date = models.DateTimeField(auto_now_add=True)

    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doorprize"
        ordering = ["-creation_date"]

    def __str__(self):
        return f"{self.prize_name} - {self.id_event.name}"


# =========================================================
# HISTORY WINNER
# =========================================================

class DoorprizeWinner(models.Model):

    id_event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="winner_histories"
    )

    id_doorprize = models.ForeignKey(
        Doorprize,
        on_delete=models.CASCADE,
        related_name="winner_histories"
    )

    id_participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="winner_histories"
    )

    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "doorprize_winner"
        ordering = ["-creation_date"]

    def __str__(self):
        return (
            f"{self.id_participant.name} "
            f"- "
            f"{self.id_doorprize.prize_name}"
        )
