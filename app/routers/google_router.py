from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="templates")
from oauth import get_oauth

oauth = get_oauth()
google_router = APIRouter()


@google_router.get("/login/google")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, url)


# Define a list of allowed email addresses
ALLOWED_EMAILS = ["aarjav.jain@gmail.com", "mojamil2000@gmail.com", "adilsaheil1999@gmail.com"]

@google_router.get('/auth', name='auth')
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
