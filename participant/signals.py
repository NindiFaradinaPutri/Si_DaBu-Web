# participant/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Participant, Notifications

@receiver(post_save, sender=Participant)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notifications.objects.create(
            participant_id=instance,
            event_id=instance.id_event,
            is_read=False
        )