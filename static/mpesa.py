import requests
from datetime import datetime

def generate_timestamp():
    # Get the current date and time
    current_datetime = datetime.now()
    # Format the date and time as a string
    timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def initiate_mpesa_transaction(amount, phone_number):
    # Make API call to initiate M-Pesa transaction
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": "5G86nwQ35p8lUdyAOsysVPXjlkhh",
        "Content-Type": "application/json",
    }
    payload = {
        "BusinessShortCode": "174379",
        "Password": "roderick2024",
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "YOUR_SHORTCODE",
        "PhoneNumber": phone_number,
        "CallBackURL": "YOUR_CALLBACK_URL",
        "AccountReference": "YOUR_REFERENCE",
        "TransactionDesc": "Payment for XYZ",
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
