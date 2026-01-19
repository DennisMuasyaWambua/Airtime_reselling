from rest_framework import serializers
from .models import Transaction, CustomerSession

class AirtimeTopUpRequestSerializer(serializers.Serializer):
    """Serializer for incoming airtime top-up requests (client input)"""
    recipient_phone_number = serializers.CharField(max_length=15)
    amount = serializers.IntegerField(min_value=1)
    session = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields=['recipient_phone_number','session','amount', 'status']

class CustomerSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSession
        fields = ['session_key', 'ip_address_hash', 'user_agent_hash']