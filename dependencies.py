from fastapi import Depends, HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from backend.data.credentials import ACCESS_SECRET_KEY,REFRESH_SECRET_KEY,Mysql_password,Database_Name
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import pymysql
DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd=Mysql_password,
    database=Database_Name,
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)
cursor=DB.cursor()


# ---------------------------
#  AUTHENTICATION SECTION
# ---------------------------

ACCESS_SECRET_KEY =ACCESS_SECRET_KEY      # separate key for access
REFRESH_SECRET_KEY = REFRESH_SECRET_KEY    # separate key for refresh
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Login")

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
# "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZ21haWwuY29tIiwiZXhwIjoxNzYwNTM1NjIwfQ.HscVrTxF07U6RfG3P3sasra99nO35V30rK3bDd23ybY"
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHJpbmdAZ21haWwuY29tIiwiZXhwIjoxNzYxMTM4NjIwfQ.f_AaLkU4NihiWn2qVhqq6PhoOhvqNxkFEO19lH8cBWQ"