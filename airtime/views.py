from django.utils.crypto import get_random_string
import logger, hashlib, secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from airtime.mpesa import Mpesa
from .serializers import CustomerSerializer, CustomerSessionSerializer, AirtimeTopUpRequestSerializer
from .models import CustomerSession
import logging
# Create your views here.
logger = logging.getLogger(__name__)

class DealerFiscalReportView(APIView):
    pass
class AirtimeTopUpView(APIView):
    mpesa = Mpesa()
    serializer_class = CustomerSerializer 
    session_serializer_class = CustomerSessionSerializer
    session = None
    def post(self, request):
        # Logic for handling airtime top-up requests
        self.mpesa.get_access_token()

        # Use the new request serializer for validation
        request_serializer = AirtimeTopUpRequestSerializer(data=request.data)
        if request_serializer.is_valid():
            customer_number = request_serializer.validated_data['recipient_phone_number']
            amount = request_serializer.validated_data['amount']
            session_key = request_serializer.validated_data.get('session')

            # Get or validate session
            session_obj = None
            if session_key:
                try:
                    session_obj = CustomerSession.objects.get(session_key=session_key)
                except CustomerSession.DoesNotExist:
                    logger.warning(f"Invalid session key provided: {session_key}")
                    # Continue without session

            # Initiate airtime top-up
            top_up = self.mpesa.airtime_top_up(customer_number, amount)
            logger.info(f"Airtime top-up response: {top_up}")
            logger.info(f"SESSION KEY: {session_key}")
            logger.info(f"Request data: {request.data}")

            if top_up.get('responseStatus') == '200':
                # Save transaction to db here
                transaction_data = {
                    'recipient_phone_number': customer_number,
                    'amount': amount,
                    'status': 'COMPLETED'
                }
                if session_obj:
                    transaction_data['session'] = session_obj.id

                transaction_serializer = self.serializer_class(data=transaction_data)
                if transaction_serializer.is_valid():
                    transaction_serializer.save()
                    return Response({"message":"Airtime top-up successful","safaricom_response":f"{top_up}"}, status=200)
                else:
                    logger.error(f"Transaction serializer errors: {transaction_serializer.errors}")
                    return Response(transaction_serializer.errors, status=500)
            else:
                # Handle failed top-up
                logger.error(f"Airtime top-up failed: {top_up}")
                return Response({
                    "message": "Airtime top-up failed",
                    "safaricom_response": top_up
                }, status=400)
        else:
            return Response(request_serializer.errors, status=400)
        
        # self.mpesa.airtime_top_up("712345678", 1000)
    def get(self, request):
       # get users Ip address and user agent
       ip_address = request.META.get('REMOTE_ADDR')
       user_agent = request.META.get('HTTP_USER_AGENT')
       logger.info(f"IP ADDRESSS: {ip_address}, USER AGENT: {user_agent}")
       # create user session ke712345678y , ip address hash, user agent hash
       session_key = get_random_string(length = 32)
       self.session = session_key
       ip_address_hash = hashlib.sha256(ip_address.encode()).hexdigest()
       user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()
       logger.info(f"SESSION KEY: {session_key},\nIP ADDRESSS HASH: {ip_address_hash},\nUSER AGENT HASH: {user_agent_hash}")
       #save session to db here
       session_serializer = self.session_serializer_class(data={
           'session_key': session_key,
           'ip_address_hash': ip_address_hash,
           'user_agent_hash': user_agent_hash
       })
       if session_serializer.is_valid():
           session_serializer.save()
           return Response({
               "message": "Airtime Top-up Service is running",
               "session_key": session_key
           }, status=status.HTTP_200_OK)
       else:
           logger.error(f"Session serializer errors: {session_serializer.errors}")
           return Response({
               "message": "Failed to create session",
               "errors": session_serializer.errors
           }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)