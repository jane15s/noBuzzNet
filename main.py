from urllib.parse import urlparse

from fastapi import FastAPI, Form
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from db import init_db, db_session
from models import Link, User
from authlib.integrations.starlette_client import OAuth

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()
pwd_context = CryptContext(schemes=["bcrypt"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/login")
async def login_check(request: Request, email: str = Form(...), password: str = Form(...)):
    user = db_session.query(User).filter_by(email=email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Помилка авторизації"})
    request.session["user_id"] = user.id
    request.session["user_name"] = user.name
    return RedirectResponse(url="/", status_code=303)

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")

@app.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    hashed = pwd_context.hash(password[:72])
    user = User(name=name, email=email, hashed_password=hashed, auth_provider="local")
    db_session.add(user)
    db_session.commit()

    default_link = Link(link="https://www.google.com", description="Пошук в інтернеті", icon="https://www.google.com/favicon.ico", owner=user.id)
    db_session.add(default_link)
    db_session.commit()

    return RedirectResponse(url="/login", status_code=303)

@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_via_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info =token.get("userinfo")

    if not user_info:
        user_info = await oauth.google.parse_id_token(request, token)
    email = user_info["email"]
    name = user_info.get("name", "Google User")

    user = db_session.query(User).filter_by(email=email).first()
    new_user = False
    if not user:
        user = User(name=name, email=email, auth_provider="google")
        db_session.add(user)
        db_session.flush()
        new_user = True

    if new_user:
        default_link = Link(link="https://www.google.com", description="Пошук в інтернеті",
                        icon="https://www.google.com/favicon.ico", owner=user.id)
        db_session.add(default_link)

    db_session.commit()

    request.session["user_id"] = user.id
    request.session["user_name"] = user.name

    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/")
async def home(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="login", status_code=303)
    links = db_session.query(Link).filter_by(owner=user_id).all()
    return templates.TemplateResponse(request=request, name="base.html", context={"links": links})

@app.get("/add_link")
async def adding_link(request: Request):
    return templates.TemplateResponse(request=request, name="add_link.html")

@app.post("/add_link")
async def add_link(request: Request, name: str = Form(...), url = Form(...)):
    user_id = request.session.get("user_id")
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    favicon = f"{base_url}/favicon.ico"
    new_link = Link(link=url, description=name, icon=favicon, owner=user_id)
    db_session.add(new_link)
    db_session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/edit_link/{link_id}")
async def editing_link(request: Request, link_id: int):
    link = db_session.query(Link).filter_by(id=link_id).first()
    return templates.TemplateResponse(request=request, name="edit_link.html", context={"link": link})

@app.post("/edit_link/{link_id}")
async def edit_link(request: Request, link_id: int, name: str = Form(...), url = Form(...)):
    link = db_session.query(Link).filter_by(id=link_id).first()
    link.description = name
    link.link = url
    db_session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete_link/{link_id}")
async def delete_link(link_id: int):
    link_to_delete = db_session.get(Link, link_id)
    db_session.delete(link_to_delete)
    db_session.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
