import os
from fastapi import UploadFile
import httpx
import csv


account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

async def send_sms_async(to, body):
    # Twilio API details

    from_number = '+447723581588'

    url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
    auth = (account_sid, auth_token)
    data = {
        'From': from_number,
        'To': to,
        'Body': body
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, auth=auth)
        return response

async def process_csv(csv_file: UploadFile):
    # Assuming the CSV has 'user_name' and 'user_phone_number' columns
    await csv_file.seek(0)  # Reset file pointer to the beginning
    reader = csv.DictReader([line.decode() for line in csv_file.file])

    for row in reader:
        user_name = row['user_name']
        user_phone_number = row['user_phone_number']
        print(user_name)
        print(user_phone_number)

        message_body = f"Hello {user_name}, this is a message from our service."

        # Send SMS asynchronously
        await send_sms_async(user_phone_number, message_body)

