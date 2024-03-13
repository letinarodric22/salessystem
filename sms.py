# works with both python 2 and 3
from __future__ import print_function
from main import adduser


import africastalking

class SMS:
    def __init__(self):
        # Set your app credentials
        self.username = "savvyTech"
        self.api_key = "b4e42ffe9cb0ba29fd5c85187a897ebb43bf59be68bd9ee55a87c8e5678ef896"

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS
# sms.py

import africastalking

class SMS:
    def __init__(self):
        # Set your app credentials
        self.username = "savvyTech"
        self.api_key = "b4e42ffe9cb0ba29fd5c85187a897ebb43bf59be68bd9ee55a87c8e5678ef896"

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def send(self, full_name, phone):
        # Set the number you want to send to in international format
        recipient = f"+{phone}"

        # Customize your message with the user's full name
        message = f"Dear {full_name}, welcome to our platform! Your registration is successful."

        try:
            # Hit send and take care of the rest.
            response = self.sms.send(message, [recipient])
            print(response)
        except Exception as e:
            print('Encountered an error while sending: %s' % str(e))

    def send(self, full_name, phone):
        # Set the numbers you want to send to in international format
        recipients = [str(phone)]

        # Set your message
        message = f"Dear {full_name}, welcome to our platform! Your registration is successful."

        # Set your shortCode or senderId
        # sender = "GroupApp"
        try:
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, recipients)
            print(response)
        except Exception as e:
            print('Encountered an error while sending: %s' % str(e))

if __name__ == '__main__':
    SMS().send()
