import os
import json
from uuid import uuid4
from datetime import datetime,timedelta
#import pandas as pda
import shutil
from django.conf import settings
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError
from decimal import Decimal

def path_and_rename(instance, filename):
    upload_to = instance.upload_to
    ext = filename.split('.')[-1]

    #filename = '{}.{}'.format(instance.file_rename, ext)
    filename = '{}.{}'.format(instance.filename.split('.')[0], ext)

    return os.path.join(upload_to,filename)

def path_photo(instance, photoname):
    upload_photo_to = instance.upload_photo_to
    ext = photoname.split('.')[-1]

    photoname = '{}.{}'.format(instance.photo_rename, ext)

    return os.path.join(upload_photo_to,photoname)

def path_attachment(instance, filename):
    upload_file_to = instance.upload_file_to
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format(instance.file_rename, ext)

    return os.path.join(upload_file_to,filename)

def path_video(instance, videoname):
    upload_video_to = instance.upload_video_to
    ext = videoname.split('.')[-1]

    videoname = '{}.{}'.format(instance.video_rename, ext)

    return os.path.join(upload_video_to,videoname)

def get_form_by_pkid(model, modelForm, pkid):
    if model.objects.filter(id = pkid).exists():
        data = model.objects.get(id = pkid)
        returnForm = modelForm(instance=data)
    else:
        returnForm = modelForm()
    return returnForm

def get_form_by_user(model, modelForm, userId):
    if model.objects.filter(user_id = userId).exists():
        data = model.objects.get(user_id = userId)
        returnForm = modelForm(instance=data)
    else:
        returnForm = modelForm()
    return returnForm

def get_form_by_service(model, modelForm, serviceId):
    if model.objects.filter(service_id = serviceId).exists():
        data = model.objects.get(service_id = serviceId)
        returnForm = modelForm(instance=data)
    else:
        returnForm = modelForm()
    return returnForm

def get_model_by_pkid(model,pkid):
    if model.objects.filter(id = pkid).exists():
        data = model.objects.get(id = pkid)
    else:
        data = model()
    return data
