from http.client import responses
from urllib.parse import urlparse
import requests

from fastapi import FastAPI, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import os

from app.db import init_db, db_session
from app.models import Link

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

init_db()

@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(request=request, name="registration.html")

@app.post("/register")
async def register():
    pass

@app.get("/login")
async def login():
    pass

@app.get("/logout")
async def logout():
    pass

@app.get("/")
async def home(request: Request):
    links = db_session.query(Link).all()
    return templates.TemplateResponse(request=request, name="base.html", context={"links": links})

@app.get("/add_link")
async def adding_link(request: Request):
    return templates.TemplateResponse(request=request, name="add_link.html")

@app.post("/add_link")
async def add_link(name: str = Form(...), url = Form(...)):
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    favicon = f"{base_url}/favicon.ico"
    new_link = Link(link=url, description=name, icon=favicon)
    db_session.add(new_link)
    db_session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_link/{link_id}")
async def delete_link(link_id: int):
    link_to_delete = db_session.get(Link, link_id)
    db_session.delete(link_to_delete)
    db_session.commit()
    return RedirectResponse(url="/", status_code=303)


