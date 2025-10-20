from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import pymysql
from fastapi.middleware.cors import CORSMiddleware

# ==========================================================
#                  CONFIGURATION
# ==========================================================
ACCESS_SECRET_KEY = "YOUR_ACCESS_SECRET_KEY"
REFRESH_SECRET_KEY = "YOUR_REFRESH_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

app = FastAPI(title="Cookie-Based Auth Example")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# --- MySQL connection ---
DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd="your_mysql_password",
    database="your_database_name",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
cursor = DB.cursor()

# ==========================================================
#                   MODELS
# ==========================================================
class UserCreate(BaseModel):
    Username: str
    Email: str
    Password: str
    Role: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================================
#                   UTILITY FUNCTIONS
# ==========================================================
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, secret: str) -> TokenData:
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==========================================================
#               AUTHENTICATION ROUTINES
# ==========================================================
# Register user
@app.post("/register")
def register_user(user: UserCreate):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (user.Email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_pwd_hash(user.Password)
    cursor.execute(
        "INSERT INTO USERS (Username, PasswordHash, Roles, Email, is_active) VALUES (%s, %s, %s, %s, %s)",
        (user.Username, hashed_password, user.Role, user.Email, True)
    )
    return {"message": "User created successfully"}

# Login – set cookies
@app.post("/login")
def login(response: Response, form_data: UserCreate):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (form_data.Email,))
    user = cursor.fetchone()
    if not user or not verify_pwd(form_data.Password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Inactive user")

    access_token = create_access_token({"sub": user["Email"]})
    refresh_token = create_refresh_token({"sub": user["Email"]})

    # Set cookies
    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, secure=False, samesite="lax",  # secure=True in production
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS*24*3600
    )

    return {"message": "Login successful"}

# Logout – delete cookies
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# Refresh access token
revoked_tokens = set()

@app.post("/refresh")
def refresh(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token in revoked_tokens:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    token_data = verify_token(refresh_token, REFRESH_SECRET_KEY)
    email = token_data.email

    new_access_token = create_access_token({"sub": email})
    new_refresh_token = create_refresh_token({"sub": email})

    revoked_tokens.add(refresh_token)

    response.set_cookie(
        key="access_token", value=new_access_token,
        httponly=True, secure=False, samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    response.set_cookie(
        key="refresh_token", value=new_refresh_token,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS*24*3600
    )
    return {"message": "Tokens refreshed"}

# Get current user from cookies
def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_data = verify_token(access_token, ACCESS_SECRET_KEY)
    cursor.execute("SELECT * FROM USERS WHERE Email=%s", (token_data.email,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Example protected route
@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["Email"], "username": current_user["Username"], "role": current_user["Roles"]}
