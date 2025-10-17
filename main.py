from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
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

# --- CORS Middleware (for frontend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MySQL Connection ---
DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd="Bineli26",
    database="Order_System",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
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
#                 AUTHENTICATION SECTION
# ==========================================================

ACCESS_SECRET_KEY = "secret_access_key"      # separate key for access
REFRESH_SECRET_KEY = "secret_refresh_key"    # separate key for refresh
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

# ---------- MODELS ----------
class UserCreate(BaseModel):
    Username: str
    Email: str
    Password: str
    Role: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# ==========================================================
#                 UTILITY FUNCTIONS
# ==========================================================
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, secret: str):
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==========================================================
#                 USER DEPENDENCIES
# ==========================================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = verify_token(token, ACCESS_SECRET_KEY)
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (token_data.email,))
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

# Temporary store for revoked tokens (in-memory)
revoked_tokens = set()

@app.post("/register")
def register_user(user: UserCreate):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (user.Email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = get_pwd_hash(user.Password)
    user_command = """INSERT INTO USERS (Username, PasswordHash, Roles, Email, is_active)
                      VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(user_command, (user.Username, hashed_password, user.Role, user.Email, True))
    DB.commit()
    return {"message": "User created successfully"}

# 
@app.post("/Login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (form_data.username,))
    user = cursor.fetchone()

    if not user or not verify_pwd(form_data.password, user["PasswordHash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Inactive user")

    # Generate tokens
    access_token = create_access_token(data={"sub": user["Email"]})
    refresh_token = create_refresh_token(data={"sub": user["Email"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@app.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str):
    """Use refresh token to get a new access + refresh token."""
    if refresh_token in revoked_tokens:
        raise HTTPException(status_code=401, detail="This refresh token has been revoked")

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Create new tokens
    new_access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})

    # Revoke old refresh token
    revoked_tokens.add(refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@app.post("/logout")
def logout(refresh_token: str):
    """Invalidate refresh token when logging out."""
    revoked_tokens.add(refresh_token)
    return {"message": "You have been logged out. Token revoked."}


# ==========================================================
#                 USER MANAGEMENT
# ==========================================================
@app.get("/user", dependencies=[Depends(get_current_active_user)])
def get_all_users():
    cursor.execute("SELECT UserID, Username, Email, Roles, is_active FROM USERS")
    result = cursor.fetchall()
    return {"users": result}


@app.put("/update_user/{user_id}")
def update_user(user_id: int, user: UserCreate, current_user: dict = Depends(require_role(["admin"]))):
    hashed_pwd = get_pwd_hash(user.Password)
    user_command = """UPDATE USERS
                      SET Username=%s, PasswordHash=%s, Roles=%s, Email=%s
                      WHERE UserID=%s"""
    cursor.execute(user_command, (user.Username, hashed_pwd, user.Role, user.Email, user_id))
    DB.commit()
    return {"message": f"User {user_id} updated"}


@app.delete("/delete_user/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_role(["admin"]))):
    cursor.execute("DELETE FROM USERS WHERE UserID=%s", (user_id,))
    DB.commit()
    return {"message": f"User {user_id} deleted"}


@app.get("/greeting")
def greeting():
    return {"message": "Welcome!"}
