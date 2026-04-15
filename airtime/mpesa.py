import os, requests,json,base64
from constants import DARAJA_ENDPOINTS as daraja_endpoints

class Mpesa:
    def __init__(self):
        self.consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')
        self.dealer_number = os.environ.get('DEALERNUMBER')
        self.dealer_pin = os.environ.get('DEALERPIN')
        self.access_token = None

        print("Consumer Key present:", bool(self.consumer_key))
        print("Consumer Secret present:", bool(self.consumer_secret))
        print("Dealer Number present:", bool(self.dealer_number))
        print("Dealer PIN present:", bool(self.dealer_pin))

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
        if not self.access_token:
            print("ERROR: No access token available. Call get_access_token() first.")
            return {"error": True, "details": "No access token available"}

        # Check if dealer credentials are configured
        if not self.dealer_number or not self.dealer_pin:
            print("ERROR: Dealer credentials not configured. Set DEALERNUMBER and DEALERPIN environment variables.")
            return {"error": True, "details": "Dealer credentials not configured"}

        # Encode the PIN in base64
        encoded_pin = base64.b64encode(self.dealer_pin.encode()).decode()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "senderMsisdn": self.dealer_number,
            "amount": f"{amount}",
            "servicePin": encoded_pin,
            "receiverMsisdn": customer_number
        }
        payload_data = json.dumps(payload, indent=2)
        print("Airtime Top-Up Payload:", payload_data)
        print("Access Token being used:", self.access_token[:20] + "..." if len(self.access_token) > 20 else self.access_token)
        airtime_url = daraja_endpoints['airtime_topup']

        try:
            response = requests.post(airtime_url, headers=headers, json=payload)
            print("SERVER RESPONSE", str(response.status_code)+" \n"+response.reason)

            # Print response body for debugging
            print("Response body:", response.text)

            response.raise_for_status()
            data = response.json()
            print("Airtime Top-Up Response:", json.dumps(data, indent=2))
            return data
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e}")
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")
            # Return the error details instead of raising
            try:
                error_data = response.json()
                return {"error": True, "status_code": response.status_code, "details": error_data}
            except:
                return {"error": True, "status_code": response.status_code, "details": response.text}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"error": True, "details": str(e)}

  



# mpesa = Mpesa()
# mpesa.get_access_token()
# mpesa.airtime_top_up("712345678",1000)