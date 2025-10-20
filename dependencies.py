from fastapi import Depends, HTTPException, Cookie
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import pymysql

# ---------------------------
#  DATABASE CONNECTION
# ---------------------------
from backend.data.credentials import ACCESS_SECRET_KEY, REFRESH_SECRET_KEY, Mysql_password, Database_Name

DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd=Mysql_password,
    database=Database_Name,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
cursor = DB.cursor()

# ---------------------------
#  AUTH CONFIGURATION
# ---------------------------
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ---------------------------
#  MODELS
# ---------------------------
class TokenData(BaseModel):
    email: Optional[str] = None

# ---------------------------
#  UTILITY FUNCTIONS
# ---------------------------
def verify_pwd(plain_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
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

# ---------------------------
#  DEPENDENCIES
# ---------------------------
def get_current_user(access_token: str = Cookie(None)):
    """
    Get the current user from the HTTP-only cookie `access_token`.
    Raises 401 if token is missing, expired, or invalid.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token_data = verify_token(access_token, ACCESS_SECRET_KEY)
    cursor.execute("SELECT * FROM USERS WHERE Email=%s", (token_data.email,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Ensures that the current user is active.
    """
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Inactive user")
    return current_user

def require_role(allowed_roles: list):
    """
    Dependency to enforce role-based access control.
    Usage: Depends(require_role(["admin", "manager"]))
    """
    def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user["Roles"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return role_checker
