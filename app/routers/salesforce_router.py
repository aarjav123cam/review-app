from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuthError
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import httpx
from oauth import get_oauth

oauth = get_oauth()
templates = Jinja2Templates(directory="templates")


salesforce_router = APIRouter()

@salesforce_router.get("/login/salesforce")
async def login_salesforce(request: Request):
    redirect_uri = request.url_for('auth_salesforce')
    return await oauth.salesforce.authorize_redirect(request, redirect_uri)


@salesforce_router.get('/auth/salesforce')
async def auth_salesforce(request: Request):
    try:
        token = await oauth.salesforce.authorize_access_token(request)
    except OAuthError as e:
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )

    # Now, use the access token to query the Salesforce UserInfo endpoint
    userinfo_endpoint = "https://login.salesforce.com/services/oauth2/userinfo"
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(userinfo_endpoint, headers=headers)


    # data_endpoint = "https://jasreviewapp-dev-ed.develop.my.salesforce.com/services/data/v50.0/recent"
    # async with httpx.AsyncClient() as client:
    #     response2 = await client.get(data_endpoint, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        # Process user_info here
        # ...
        if user_info:  # Add your user validation logic here
            request.session['user'] = dict(user_info)
            return RedirectResponse(url='/welcome')
        else:
            # Handle the case where user info is not available
            request.session.pop('user', None)
            return RedirectResponse(url='/?message=unauthorized')
    else:
        # Handle errors (e.g., invalid response)
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': 'Failed to fetch user info'}
        )
