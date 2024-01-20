import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()  # This loads the environment variables from .env

SF_ID = os.getenv("SF_ID")
SF_SECRET = os.getenv("SF_SECRET")

secret_key = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

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

oauth.register(
    name='salesforce',
    client_id=SF_ID,
    client_secret=SF_SECRET,
    authorize_url='https://login.salesforce.com/services/oauth2/authorize',
    authorize_params=None,
    access_token_url='https://login.salesforce.com/services/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri='https://twilio-app-owc5ogwcaa-nw.a.run.app/auth/salesforce',  # Change to your callback URL
    client_kwargs={'scope': 'email profile'},
)



def get_oauth():
    return oauth