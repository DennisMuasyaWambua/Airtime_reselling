import os, requests,json,base64
from airtime.constants import DARAJA_ENDPOINTS as daraja_endpoints

class Mpesa:
    def __init__(self):
        self.consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')
        self.dealer_number = os.environ.get('DEALERNUMBER')
        self.dealer_pin = os.environ.get('DEALERPIN')
        self.access_token = None

        print("Consumer Key present",bool(self.consumer_key))
        print("Consumer Secret present",bool(self.consumer_secret))

    def get_access_token(self):
        """Worked after changing the keys"""
        auth_url = daraja_endpoints['access_token']
        
        auth_header = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        print("Auth Header:",auth_header)
        headers = {
            "Authorization": f"Basic {auth_header}"
        }
        params = {
            "grant_type": "client_credentials"
        }
        try:
            response = requests.get(auth_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            token = data.get('access_token')
            self.access_token = token
            print("Access Token:", self.access_token)
            return self.access_token

        except requests.exceptions.RequestException as e:
            print("Error during request:", e)
            return None

    def airtime_top_up( self, customer_number, amount):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "senderMsisdn":"727501860",#self.dealer_number,
            "amount":f"{amount}",
            "servicePin":"MTE4NQ==",#base64.b64encode(self.dealer_pin.encode()).decode(),
            "receiverMsisdn":customer_number
        }
        payload_data = json.dumps(payload, indent=2)    
        print("Airtime Top-Up Payload:", payload_data)
        airtime_url = daraja_endpoints['airtime_topup']
     
        response = requests.post(airtime_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("SERVER RESPONSE", str(response.status_code)+" \n"+response.reason)
        print("Airtime Top-Up Response:", json.dumps(data, indent=2))
        return data

  



# mpesa = Mpesa()
# mpesa.get_access_token()
# mpesa.airtime_top_up("712345678",1000)