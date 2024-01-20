from fastapi import APIRouter, Request, File, UploadFile
from typing import Annotated
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from twilioSms.csv_process import process_csv


templates = Jinja2Templates(directory="templates")
general_router = APIRouter()


@general_router.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')
    message = request.query_params.get('message', '')
    return templates.TemplateResponse(
        name="home.html",
        context={"request": request, "message": message}
    )

@general_router.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )


@general_router.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    return RedirectResponse('/')

@general_router.post("/uploadfiles/")
async def create_upload_files(
        files: Annotated[
            list[UploadFile], File(description="Multiple files as UploadFile")
        ],
):
    for file in files:
        await process_csv(file)
    return {"filenames": [file.filename for file in files]}


