from fastapi.staticfiles import StaticFiles
from typing import Annotated

from fastapi import File
from fastapi.templating import Jinja2Templates

import csv
import httpx
from fastapi import UploadFile
import os
from fastapi import FastAPI, Request
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
#from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

load_dotenv()  # This loads the environment variables from .env

secret_key = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
app = FastAPI()

app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.a.run.app"])


app.mount("/static", StaticFiles(directory="static"), name="static")


oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile'
    }
)


templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')
    message = request.query_params.get('message', '')
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request, "message": message}
    )


@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )


@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


# Define a list of allowed email addresses
ALLOWED_EMAILS = ["aarjav.jain@gmail.com", "mojamil2000@gmail.com"]

@app.get('/auth', name='auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )

    user = token.get('userinfo')

    if user and user.get("email") in ALLOWED_EMAILS:
        request.session['user'] = dict(user)
        return RedirectResponse(url='welcome')
    else:
        # Log out the user and redirect to the home page with an unauthorized message
        request.session.pop('user', None)  # Clear user data from the session
        return RedirectResponse(url='/?message=unauthorized')

@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    return RedirectResponse('/')


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
    return {"filenames": [file.filename for file in files]}
