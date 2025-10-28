from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="supersecret")

templates = Jinja2Templates(directory="app/templates")



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="base.html")
