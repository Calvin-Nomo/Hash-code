from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from backend.data.credentials import ACCESS_SECRET_KEY, REFRESH_SECRET_KEY, Mysql_password, Database_Name
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import pymysql
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import client, order, order_items, reservation, payment, product, stock, table

# ==========================================================
#                 APP CONFIGURATION
# ==========================================================
app = FastAPI(title="Qrcode Order System")
# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your frontend server
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,  # very important for cookies
)

# --- MySQL Connection ---
DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd=Mysql_password,
    database=Database_Name,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
cursor = DB.cursor()

# --- Include Routers ---
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(table.router, prefix="/table", tags=["table"])

# ==========================================================
#                 AUTHENTICATION CONFIG
# ==========================================================
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ==========================================================
#                  MODELS
# ==========================================================
class UserCreate(BaseModel):
    Username: str
    Email: str
    Password: str
    Role: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================================
#                  UTILITY FUNCTIONS
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
#                  USER DEPENDENCIES
# ==========================================================
def get_current_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_data = verify_token(access_token, ACCESS_SECRET_KEY)
    cursor.execute("SELECT * FROM USERS WHERE Email=%s", (token_data.email,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user

def require_role(allowed_roles: list):
    def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user["Roles"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return role_checker

# ==========================================================
#                 AUTH ROUTES
# ==========================================================
revoked_tokens = set()

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

@app.post("/login")
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (form_data.username,))
    user = cursor.fetchone()
    if not user or not verify_pwd(form_data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Inactive user")
    
    access_token = create_access_token({"sub": user["Email"]})
    refresh_token = create_refresh_token({"sub": user["Email"]})

    response.set_cookie(
        key="access_token", value=access_token,
        httponly=True, secure=False, samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS*24*3600
    )

    return {"message": "Successfully logged in"}

@app.post("/refresh")
def refresh_access_token(response: Response, refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
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

    return {"message": "Tokens refreshed successfully"}

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# ==========================================================
#                 USER MANAGEMENT
# ==========================================================
@app.get("/user", dependencies=[Depends(require_role(['admin']))])
def get_all_users():
    cursor.execute("SELECT UserID, Username, Email, Roles, is_active FROM USERS")
    result = cursor.fetchall()
    return {"users": result}

@app.put("/update_user/{user_id}")
def update_user(user_id: int, user: UserCreate, current_user: dict = Depends(require_role(["admin"]))):
    hashed_pwd = get_pwd_hash(user.Password)
    cursor.execute(
        "UPDATE USERS SET Username=%s, PasswordHash=%s, Roles=%s, Email=%s WHERE UserID=%s",
        (user.Username, hashed_pwd, user.Role, user.Email, user_id)
    )
    return {"message": f"User {user_id} updated"}

@app.delete("/delete_user/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_role(["admin"]))):
    cursor.execute("DELETE FROM USERS WHERE UserID=%s", (user_id,))
    return {"message": f"User {user_id} deleted"}

@app.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["Email"], "username": current_user["Username"], "role": current_user["Roles"]}

@app.get("/greeting")
def greeting():
    return {"message": "Welcome!"}
