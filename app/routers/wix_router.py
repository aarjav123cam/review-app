from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

wix_router = APIRouter()


WIX_CLIENT_ID= os.getenv("WIX_CLIENT_ID")
WIX_CLIENT_SECRET=os.getenv("WIX_CLIENT_SECRET")

REDIRECT_URL = "https://twilio-app-owc5ogwcaa-nw.a.run.app/auth/wix"

@wix_router.get("/initiate-wix-installation")
async def initiate_wix_installation(request: Request):
    # Construct the Wix installation URL
    wix_install_url = f"https://www.wix.com/installer/install?appId={WIX_CLIENT_ID}&redirectUrl={REDIRECT_URL}"
    # Redirect the user to the Wix installation UR
    return RedirectResponse(url=wix_install_url)


@wix_router.get("/auth/wix")
async def auth_wix(request: Request):
    # Extract the parameters from the query
    code = request.query_params.get('code')
    instance_id = request.query_params.get('instanceId')

    # Optional: Verify the state parameter if you used it in the previous step
    # expected_state = "your-unique-state"  # The state you sent to Wix
    # if received_state != expected_state:
    #     raise HTTPException(status_code=400, detail="State mismatch. Potential CSRF.")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    # Exchange the authorization code for an access token
    access_token, refresh_token = await exchange_code_for_token(code)


    # Handle the tokens (e.g., store them, associate them with the instance_id/user session, etc.)
    # ...


    redirect_url = f"/wix/booking?access_token={access_token}"
    return RedirectResponse(redirect_url)

@wix_router.get("/wix/booking")
async def wix_booking(access_token: str, fromDate: str = None, toDate: str = None):
    # If fromDate and toDate are not provided, set them to default values
    if not fromDate:
        fromDate = datetime.utcnow().date().isoformat()  # Today's date in ISO format
    if not toDate:
        toDate = (datetime.utcnow().date() + timedelta(days=365)).isoformat()  # One year from today in ISO format

    url = "https://www.wixapis.com/members/v1/members"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    # payload = {
    #     "fromDate": fromDate,
    #     "toDate": toDate,
    #     "query": {},
    #     "type": "EVENT",  # You can customize these fields as needed
    #     "instances": True,
    #     "includeExternal": False
    #
    # }


    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    response.raise_for_status()
    sessions_data = response.json()
    return sessions_data


async def exchange_code_for_token(code: str):
    url = "https://www.wixapis.com/oauth/access"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "authorization_code",
        "client_id": WIX_CLIENT_ID,
        "client_secret": WIX_CLIENT_SECRET,
        "code": code
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    token_data = response.json()


    return token_data.get("access_token"), token_data.get("refresh_token")

async def refresh_access_token(refresh_token: str):
    url = "https://www.wixapis.com/oauth/access"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "refresh_token",
        "client_id": WIX_CLIENT_ID,
        "client_secret": WIX_CLIENT_SECRET,
        "refresh_token": refresh_token
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
    response.raise_for_status()
    token_data = response.json()
    return token_data.get("access_token"), token_data.get("refresh_token"), token_data.get("expires_in")
