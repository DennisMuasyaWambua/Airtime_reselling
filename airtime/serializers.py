from rest_framework import serializers
from .models import Transaction, CustomerSession

class CustomerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Transaction
        fields=['recipient_phone_number','session','amount', 'status']

class CustomerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSession
        fields = ['session_key', 'ip_address_hash', 'user_agent_hash']