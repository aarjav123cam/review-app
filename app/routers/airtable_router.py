AIRTABLE_CLIENT_ID = "ee1dd32c-fa6a-469f-a347-c21e3a9fe078"
AIRTABLE_CLIENT_SECRET = "72b9bc7d32de1e2ae73a6ae6392ade11290578f53990870ff06997ba1429563a"
SCOPE = 'data.records:read user.email:read'

from fastapi import FastAPI, Request, HTTPException, Depends, APIRouter
from fastapi.responses import RedirectResponse
import httpx
import os
import secrets
import hashlib
import base64

airtable_router = APIRouter()
# CLIENT_ID = os.getenv('AIRTABLE_CLIENT_ID')
# CLIENT_SECRET = os.getenv('AIRTABLE_CLIENT_SECRET')
REDIRECT_URI = 'https://twilio-app-owc5ogwcaa-nw.a.run.app/auth/airtable'
AUTHORIZATION_ENDPOINT = 'https://airtable.com/oauth2/v1/authorize'
TOKEN_ENDPOINT = 'https://airtable.com/oauth2/v1/token'


def generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)[:128]

def generate_code_challenge(code_verifier: str) -> str:
    # Generate SHA256 hash of the code_verifier
    hashed = hashlib.sha256(code_verifier.encode()).digest()
    # Base64-url-encode the hash
    return base64.urlsafe_b64encode(hashed).decode().rstrip("=")

def generate_state() -> str:
    return secrets.token_urlsafe(32)[:64]




@airtable_router.get('/login/airtable')
def login():
    # Generate a cryptographically secure state and code_verifier
    state = generate_state()
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)  # Generate the code_challenge from code_verifier
    # Construct the authorization URL
    auth_url = (
        f'{AUTHORIZATION_ENDPOINT}'
        f'?client_id={AIRTABLE_CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&response_type=code'
        f'&scope={SCOPE}'
        f'&state={state}'
        f'&code_challenge={code_challenge}'
        f'&code_challenge_method=S256'
    )
    # Redirect the user to the authorization URL
    #return RedirectResponse(auth_url)

    # Redirect the user to the authorization URL
    response = RedirectResponse(auth_url)
    # Store code_verifier and state in user's session or a secure place for later verification
    response.set_cookie(key='code_verifier', value=code_verifier, httponly=True)
    response.set_cookie(key='state', value=state, httponly=True)
    return response

@airtable_router.get('/auth/airtable')
async def callback(code: str, state: str, request: Request):
    # Verify state and code_challenge here
    stored_state = request.cookies.get('state')
    code_verifier = request.cookies.get('code_verifier')

    if not stored_state or not code_verifier or state != stored_state:
        raise HTTPException(status_code=400, detail="State or code_verifier mismatch")

    credentials = f"{AIRTABLE_CLIENT_ID}:{AIRTABLE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_value = f"Basic {encoded_credentials}"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        "Authorization": auth_value
    }
    # Exchange code for an access token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': AIRTABLE_CLIENT_ID,
        'code_verifier': code_verifier,  # The code_verifier used when generating code_challenge
        'client_secret': AIRTABLE_CLIENT_SECRET
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_ENDPOINT, headers=headers, data=token_data)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    tokens = response.json()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    # Store the tokens securely and associate them with the user session

    if access_token and refresh_token:
        #return RedirectResponse(url=f"/refresh/airtable?refresh_token={refresh_token}")
        #return {'message': 'Authorization successful'}
        response = RedirectResponse(url="/user/airtable")
        response.set_cookie(key='access_token', value=access_token, httponly=True)
        return response

# Add more routes for your application logic and token refreshing as needed

@airtable_router.get('/user/airtable')
async def get_user_info(request: Request):
    access_token = request.cookies.get('access_token')
    headers = {
        'Authorization': f"Bearer {access_token}",
    }
    url = "https://api.airtable.com/v0/meta/whoami"
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers)

    if response.status_code != 200:
        # Handle other errors
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    return data

@airtable_router.get('/refresh/airtable')
async def refresh_access_token(refresh_token: str):
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    # Prepare headers for the token refresh request


    # Use BasicAuth for the Authorization header
    #auth = httpx.BasicAuth(AIRTABLE_CLIENT_ID, AIRTABLE_CLIENT_SECRET)
    credentials = f"{AIRTABLE_CLIENT_ID}:{AIRTABLE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth = f"Basic {encoded_credentials}"

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': auth,
    }

    # Send the token refresh request
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_ENDPOINT, data=refresh_data, headers=headers, auth=auth)

    # Check for 409 conflict error and handle appropriately
    if response.status_code == 409:
        # Implement your logic for handling token reuse conflict
        raise HTTPException(status_code=409, detail="Conflict: Refresh token was reused.")

    if response.status_code != 200:
        # Handle other errors
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # Extract the new access token and refresh token from the response
    tokens = response.json()
    new_access_token = tokens.get('access_token')
    new_refresh_token = tokens.get('refresh_token')

    # Return the new tokens
    return {'access_token': new_access_token, 'refresh_token': new_refresh_token}
