from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

import csv
import httpx
from fastapi import UploadFile
import os

account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

app = FastAPI()



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


@app.post("/uploadfiles/")
async def create_upload_files(
        files: Annotated[
            list[UploadFile], File(description="Multiple files as UploadFile")
        ],
):
    for file in files:
        await process_csv(file)
    #process_csv_files(files)
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<html>    
<head>
    <title>Upload CSV File</title>
    <link href="/static/style.css" rel="stylesheet">
</head>    
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple accept=".csv">
<input type="submit">
</form>
</body>
</html>
    """
    return HTMLResponse(content=content)