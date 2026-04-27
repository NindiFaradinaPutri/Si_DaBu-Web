from email.policy import default
import os
from django.db import models
from django.db.models import DateTimeField
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from utils.functions import *
from utils.utils import *

from authentication.models import *

from hashids import Hashids
hashid = Hashids(salt='silatama systems.', min_length=16)
