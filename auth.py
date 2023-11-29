from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from email.utils import parseaddr
from app import user_manager
from database import save

import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# set router
auth = APIRouter()
templates = Jinja2Templates(directory="templates")

# initialize login manager
login_manager = LoginManager(SECRET_KEY, token_url="/login", use_cookie=True)
login_manager.cookie_name = "session"

@login_manager.user_loader()
def load_user(email):
    return user_manager.get_user_from_email(email)

@auth.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth.post("/login")
async def handle_login(request: Request, email: str = Form(...), password: str = Form(...), remember: bool = Form(False)):
    email = email.lower()
    
    user = load_user(email)

    # check if user exists and password is correct
    if not user or not check_password_hash(user.get_password_hash(), password):
        return templates.TemplateResponse("login.html", {"request": request, "message": "Incorrect email/password."})

    # handle remember me button
    expiry_time = timedelta(days=7) if remember else timedelta(minutes=15)
    
    access_token = login_manager.create_access_token(
        data={"sub": email}, expires=expiry_time
    )
    
    # successful login
    response = RedirectResponse(url="/home", status_code=302)
    login_manager.set_cookie(response, access_token)
    
    return response

@auth.get("/logout")
def logout(user = Depends(login_manager.optional)):
    response = RedirectResponse("/login", status_code=302)
    
    # remove the cookie to log the user out
    if user is not None:
        response.delete_cookie(key="session")
    return response

@auth.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth.post("/register")
async def handle_register(request: Request, email: str = Form(...), name: str = Form(...), password: str = Form(...), repassword: str = Form(...) ):
    
    # validate email format
    if "@" not in parseaddr(email)[1]:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Invalid email format."})
    
    user = load_user(email)
    
    # check if user already exists
    if user:
        return templates.TemplateResponse("register.html", {"request": request, "message": "User already exists."})

    # verify password entered correctly
    if password != repassword:
        return templates.TemplateResponse("register.html", {"request": request, "message": "Passwords not the same."})

    # create new user and update the database
    user_manager.create_user(email, name, generate_password_hash(password))
    save()

    # successful registration
    return RedirectResponse("/login", status_code=302)