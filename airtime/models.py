from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class User(AbstractUser):
      """This is the authentication model to only be used by the admins of the system"""
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
      is_verified = models.BooleanField(default=False)
      created_at = models.DateTimeField(auto_now_add=True)

      class Meta:
            db_table = 'users'
class CustomerSession(models.Model):
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      session_key =models.CharField(max_length=64, unique=True, db_index=True)
      ip_address_hash = models.CharField(max_length=64)
      user_agent_hash = models.CharField(max_length=64)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      class Meta:
            db_table = 'customer_sessions'

class Transaction(models.Model):
      STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('AWAITING_PAYMENT', 'Awaiting Payment'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
       ]
      id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
      recipient_phone_number = models.CharField(max_length=15)
      session = models.ForeignKey(CustomerSession, on_delete=models.CASCADE, related_name='transactions')
      amount = models.IntegerField()
      status = models.CharField(max_length=20, choices=STATUS_CHOICES)
      created_at = models.DateTimeField(auto_now_add=True)
      updated_at = models.DateTimeField(auto_now=True)

      class Meta:
            db_table = 'transactions'