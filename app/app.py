from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from oauth import get_oauth
from routers import general_router, google_router, salesforce_router, wix_router, airtable_router

secret_key = os.getenv("SECRET_KEY")

app = FastAPI()

app.add_middleware(ProxyHeadersMiddleware)
app.add_middleware(SessionMiddleware, secret_key=secret_key)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.a.run.app"])


app.mount("/static", StaticFiles(directory="static"), name="static")

oauth = get_oauth()

templates = Jinja2Templates(directory="templates")

app.include_router(general_router.general_router)
app.include_router(google_router.google_router)
app.include_router(salesforce_router.salesforce_router)
app.include_router(wix_router.wix_router)
app.include_router(airtable_router.airtable_router)

