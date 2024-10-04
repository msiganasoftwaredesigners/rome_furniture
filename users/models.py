#users/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, null=True)
    username = models.CharField(_("username"), max_length=30,unique=True, null=True) 
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    facebook_url = models.URLField(_("facebook url"), blank=True)
    telegram_url = models.URLField(_("telegram url"), blank=True)
    whatsapp_url = models.URLField(_("whatsapp url"), blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    point_reward = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=30, blank=True)
    is_ordersuperuser = models.BooleanField(default=False)
  


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class UserProductLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey('store.Product', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
