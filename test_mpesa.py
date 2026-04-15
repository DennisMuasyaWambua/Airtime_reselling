#!/usr/bin/env python
"""
Test script for M-Pesa functionality
Run this script to test M-Pesa integration with current credentials
"""
import os
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airtime_api.settings')
django.setup()

from airtime.mpesa import Mpesa

def test_access_token():
    """Test getting access token from Safaricom"""
    print("=" * 60)
    print("Testing M-Pesa Access Token Generation")
    print("=" * 60)

    # Test with detailed error handling
    import base64
    import requests
    from airtime.constants import DARAJA_ENDPOINTS as daraja_endpoints

    consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
    consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')

    print(f"Consumer Key: {consumer_key[:20]}..." if consumer_key else "Consumer Key: None")
    print(f"Consumer Secret: {consumer_secret[:20]}..." if consumer_secret else "Consumer Secret: None")

    auth_url = daraja_endpoints['access_token']
    print(f"Auth URL: {auth_url}")

    auth_header = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    params = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.get(auth_url, headers=headers, params=params)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        response.raise_for_status()
        data = response.json()
        token = data.get('access_token')

        print("\n✓ SUCCESS: Access token retrieved successfully!")
        print(f"Token: {token[:20]}..." if len(token) > 20 else f"Token: {token}")

        # Now use the Mpesa class
        mpesa = Mpesa()
        mpesa.access_token = token
        return mpesa
    except requests.exceptions.RequestException as e:
        print(f"\n✗ FAILED: {e}")
        return None

def test_airtime_topup(mpesa, phone_number, amount):
    """Test airtime top-up"""
    print("\n" + "=" * 60)
    print("Testing Airtime Top-Up")
    print("=" * 60)
    print(f"Phone Number: {phone_number}")
    print(f"Amount: KES {amount}")

    result = mpesa.airtime_top_up(phone_number, amount)

    print("\n" + "-" * 60)
    print("Top-Up Result:")
    print("-" * 60)

    if result.get('error'):
        print(f"✗ FAILED: {result.get('details')}")
        if result.get('status_code'):
            print(f"Status Code: {result.get('status_code')}")
    elif result.get('responseStatus') == '200':
        print("✓ SUCCESS: Airtime top-up completed!")
        print(f"Response: {result}")
    else:
        print(f"⚠ UNKNOWN STATUS: {result}")

    return result

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("M-PESA TEST SCRIPT")
    print("=" * 60)
    print(f"Environment: {os.environ.get('ENVIRONMENT', 'Not set')}")
    print("=" * 60 + "\n")

    # Test 1: Get access token
    mpesa = test_access_token()

    if not mpesa:
        print("\n❌ Cannot proceed without access token")
        sys.exit(1)

    # Test 2: Airtime top-up (if phone number and amount provided)
    if len(sys.argv) >= 3:
        phone_number = sys.argv[1]
        amount = sys.argv[2]

        print(f"\n⚠ You are about to top-up {phone_number} with KES {amount}")
        confirm = input("Proceed? (yes/no): ")

        if confirm.lower() in ['yes', 'y']:
            test_airtime_topup(mpesa, phone_number, amount)
        else:
            print("Top-up cancelled")
    else:
        print("\n" + "=" * 60)
        print("To test airtime top-up, run:")
        print(f"python test_mpesa.py <phone_number> <amount>")
        print(f"Example: python test_mpesa.py 254712345678 10")
        print("=" * 60)

    print("\n✓ Test completed\n")
