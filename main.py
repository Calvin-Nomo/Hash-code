from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from backend.data.credentials import ACCESS_SECRET_KEY, REFRESH_SECRET_KEY, Mysql_password, Database_Name
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os, shutil
import jwt
import pymysql
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import client, order, order_items, reservation, payment, product, stock, table,notification

# ==========================================================
#                 APP CONFIGURATION
# ==========================================================
app = FastAPI(title="Qrcode Order System")
# --- CORS Middleware ---
# Liste des origines autorisées (ton frontend)
origins = [
"http://127.0.0.1:5500",
"http://127.0.0.1:8000"
# ou ton domaine exact
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # your frontend server
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


UPLOAD_DIR = "uploads"
# Serve static files at /uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- Include Routers ---
app.include_router(client.router, prefix="/client", tags=["client"])
app.include_router(order.router, prefix="/order", tags=["order"])
app.include_router(order_items.router, prefix="/order_items", tags=["order_items"])
app.include_router(reservation.router, prefix="/reservation", tags=["reservation"])
app.include_router(product.router, prefix="/product", tags=["product"])
app.include_router(payment.router, prefix="/payment", tags=["payment"])
app.include_router(stock.router, prefix="/stock", tags=["stock"])
app.include_router(table.router, prefix="/table", tags=["table"])
app.include_router(notification.router, prefix="/notification", tags=["notification"])

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
# --- Pydantic model ---
class SystemSettings(BaseModel):
    business_name: str
    business_address: str
    business_website: str
    receipt_footer: str
    show_qr: bool
class Admin_Setting(BaseModel):
    languages:str

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
def get_langauge():
        language={
    'eng':{
        'das_title':'Dashbord',
    },
    'fr':{
        'das_title':'Tableau de Bord'
    }
    }
        return


# ==========================================================
#                 AUTH ROUTES
# ==========================================================
revoked_tokens = set()

@app.post("/register")
def register_user(user: UserCreate):
    try:
        cursor.execute("SELECT * FROM USERS WHERE Email = %s", (user.Email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="User already exists")
        hashed_password = get_pwd_hash(user.Password)
        cursor.execute(
            "INSERT INTO USERS (Username,Email,PasswordHash, Roles,  is_active) VALUES (%s, %s, %s, %s, %s)",
            (user.Username,  user.Email, hashed_password, user.Role,True)
        )
    except:
        raise HTTPException(status_code=500,detail='something went wrong')
    return {"message": "User created successfully"}

@app.post("/login")
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM USERS WHERE Email = %s", (form_data.username,))
    user = cursor.fetchone()
    try :
        if not user or not verify_pwd(form_data.password, user["PasswordHash"]):
           raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.get("is_active", True):
           raise HTTPException(status_code=401, detail="Inactive user")
    
        access_token = create_access_token({"sub": user["Email"]})
        refresh_token = create_refresh_token({"sub": user["Email"]})

        response.set_cookie(
           key="access_token", value=access_token,
           httponly=True, secure=False, samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60)
        response.set_cookie(
        key="refresh_token", value=refresh_token,
        httponly=True, secure=False, samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS*24*3600 )
        # Getting the user
        cursor.execute(""" Select Roles,Username,UserID from Users Where Email = %s""",(form_data.username,))
        role=cursor.fetchone()
        return {"message": "Successfully logged in",
                "role":f"{role['Roles']}",
                "username":f"{role['Username']}",
                "user_id":f"{role["UserID"]}"
                }
    except Exception as e :
        return {"message": "error logged in"}
        # raise HTTPException(status_code=401, message="Incorrect email or password")
        

    

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
@app.get("/user/by/{user_id}")
def get_users( user_id:int):
    cursor.execute("""select p.Profile_link,u.UserID,u.Roles,u.Username,u.Email
from users u
join admin_setting p
ON
p.updated_by=u.UserID
where u.UserID=%s""",(user_id))
    result = cursor.fetchone()
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



# --- GET global settings ---
@app.get("/settings")
def get_global_settings():
    cursor.execute("SELECT * FROM system_settings ORDER BY system_id DESC LIMIT 1")
    settings = cursor.fetchone()
    if not settings:
        raise HTTPException(status_code=404, detail="No settings found")
    return settings

# --- UPDATE settings ---
@app.put("/update_settings")
def update_global_settings(settings: SystemSettings):
    cursor.execute("""Select system_id From system_settings Limit 1""")
    system_id=cursor.fetchone()
    if system_id:
        cursor.execute("""
            UPDATE system_settings
            SET business_name=%s,
                business_address=%s, business_website=%s,
                receipt_footer=%s, show_qr=%s
            WHERE system_id=%s
        """, (
            settings.business_name,
            settings.business_address, settings.business_website,
            settings.receipt_footer, settings.show_qr,system_id['system_id']
        ))
        return{'message': f'Settings updated successfully {system_id['system_id']}'

        }
    else:
        cursor.execute("""
            INSERT INTO system_settings (business_name, business_address, business_website, receipt_footer, show_qr)
            VALUES (%s,%s,%s,%s,%s)
        """, (settings.business_name, settings.business_address,
              settings.business_website, settings.receipt_footer, settings.show_qr))

    DB.commit()
    return {"message": "Settings created successfully"}



# --- ############Admin  Settings Configuration ############ ---
#  GET admin setting (personal)
@app.get("/admin/setting/{user_id}")
def get_admin_setting(user_id: int):
    try:
        cursor.execute("SELECT * FROM admin_setting WHERE updated_by = %s", (user_id,))
        setting = cursor.fetchone()

        # If not exist, create default
        if not setting:
            cursor.execute("""
                INSERT INTO admin_setting (languages,updated_by)
                VALUES ('eng', %s)
            """, (user_id,))
            DB.commit()
            cursor.execute("SELECT * FROM admin_setting WHERE updated_by = %s", (user_id,))
            setting = cursor.fetchone()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "successfully return the admin info ",
        "language": setting["languages"]
    }

# UPDATE admin setting
@app.put("/admin/setting/update/{user_id}")
def update_admin_setting(user_id: int, settings: Admin_Setting):
    cursor.execute("SELECT * FROM admin_setting WHERE updated_by = %s", (user_id,))
    exist = cursor.fetchone()

    if not exist:
        raise HTTPException(status_code=404, detail="No settings found for this admin")

    cursor.execute("""
        UPDATE admin_setting
        SET languages=%s
        WHERE updated_by=%s
    """, (settings.languages, user_id))
    DB.commit()
    return {"message": f"Settings updated successfully for admin {user_id}"}
# ajust the admin profile pictures
@app.put("/update/profile/image/{user_id}")
async def update_profile_link(user_id: int, image: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_image_path = f"{UPLOAD_DIR}/{image.filename}"

        # Check if row exists
        cursor.execute("SELECT admin_id FROM admin_setting WHERE updated_by=%s", (user_id,))
        row = cursor.fetchone()

        if row:
            # Update existing row
            cursor.execute(
                "UPDATE admin_setting SET Profile_link=%s, updated_at=NOW() WHERE updated_by=%s",
                (db_image_path, user_id)
            )
        else:
            # Insert new row
            cursor.execute(
                "INSERT INTO admin_setting (updated_by, Profile_link) VALUES (%s, %s)",
                (user_id, db_image_path)
            )

        DB.commit()

        return {
            "message": "Profile image updated successfully",
            "profile_image": db_image_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#################### Language translation



# UPDATE admin setting
@app.get("/language/{user_id}")
def get_langeuage (user_id: int):
    cursor.execute("SELECT languages FROM admin_setting WHERE updated_by = %s", (user_id,))
    exist = cursor.fetchone()
    language= {
    "en": {
        # -------------------------------
        # SIDEBAR + NAVIGATION
        # -------------------------------
        "sidebar-title": "Smart Menu",
        "nav-dashboard": "Dashboard",
        "nav-inventory": "Inventory",
        "nav-products": "Products",
        "nav-add-product": "Add New Product",
        "nav-stock": "Stock",
        "nav-category": "Category",
        "nav-reservation": "Reservation",
        "nav-table": "Table",
        "nav-users": "Users",
        "nav-all-users": "All Users",
        "nav-orders": "Orders",
        "nav-order-list": "Order List",
        "nav-qrcode": "Qrcode System",
        "nav-payment": "Payment",
        "nav-account": "Account",
        "nav-system-settings": "System Settings",

        # Navbar Search
        "search-bar-placeholder": "Search here...",

        # -------------------------------
        # PROFILE PAGE
        # -------------------------------
        "profile-config-title": "Profile Configuration",
        "btn-change-photo-text": "Change Photo",
        "user-password-label": "Password:",
        "btn-logout-text": "Logout",

        # -------------------------------
        # PRODUCT MANAGEMENT PAGE
        # -------------------------------
        "pm-title": "Product Management",
        "pm-search-placeholder": "Search product...",
        "btn-new-product": "New",

        # Table Headers
        "th-image": "Image",
        "th-name": "Name",
        "th-category": "Category",
        "th-description": "Description",
        "th-price": "Price",
        "th-action": "Action",

        # -------------------------------
        # EDIT PRODUCT POPUP
        # -------------------------------
        "edit-title": "Edit Product",
        "label-edit-name": "Name",
        "label-edit-category": "Category",
        "label-edit-price": "Price",
        "label-edit-desc": "Description",
        "label-edit-image": "Image",
        "edit-save-btn": "Save",
        "edit-cancel-btn": "Cancel",

        # -------------------------------
        # DELETE PRODUCT POPUP
        # -------------------------------
        "delete-confirm-text": "Do you want to delete this product?",
        "delete-yes-btn": "Yes",
        "delete-no-btn": "No"
    },

    "fr": {
        # -------------------------------
        # SIDEBAR + NAVIGATION
        # -------------------------------
        "sidebar-title": "Smart Menu",
        "nav-dashboard": "Tableau de Bord",
        "nav-inventory": "Inventaire",
        "nav-products": "Produits",
        "nav-add-product": "Ajouter un Produit",
        "nav-stock": "Stock",
        "nav-category": "Catégorie",
        "nav-reservation": "Réservation",
        "nav-table": "Table",
        "nav-users": "Utilisateurs",
        "nav-all-users": "Tous les Utilisateurs",
        "nav-orders": "Commandes",
        "nav-order-list": "Liste des Commandes",
        "nav-qrcode": "Système Qrcode",
        "nav-payment": "Paiement",
        "nav-account": "Compte",
        "nav-system-settings": "Paramètres du Système",

        # Navbar Search
        "search-bar-placeholder": "Chercher ici...",

        # -------------------------------
        # PROFILE PAGE
        # -------------------------------
        "profile-config-title": "Configuration du Profil",
        "btn-change-photo-text": "Modifier la Photo",
        "user-password-label": "Mot de passe:",
        "btn-logout-text": "Déconnexion",

        # -------------------------------
        # PRODUCT MANAGEMENT PAGE
        # -------------------------------
        "pm-title": "Gestion des Produits",
        "pm-search-placeholder": "Rechercher un produit...",
        "btn-new-product": "Nouveau",

        # Table Headers
        "th-image": "Image",
        "th-name": "Nom",
        "th-category": "Catégorie",
        "th-description": "Description",
        "th-price": "Prix",
        "th-action": "Action",

        # -------------------------------
        # EDIT PRODUCT POPUP
        # -------------------------------
        "edit-title": "Modifier le Produit",
        "label-edit-name": "Nom",
        "label-edit-category": "Catégorie",
        "label-edit-price": "Prix",
        "label-edit-desc": "Description",
        "label-edit-image": "Image",
        "edit-save-btn": "Enregistrer",
        "edit-cancel-btn": "Annuler",

        # -------------------------------
        # DELETE PRODUCT POPUP
        # -------------------------------
        "delete-confirm-text": "Voulez-vous supprimer ce produit ?",
        "delete-yes-btn": "Oui",
        "delete-no-btn": "Non"
    }
}

    if not exist:
        raise HTTPException(status_code=404, detail="No language found")

    DB.commit()
    return {"message": f"Settings updated successfully for admin {user_id}",
            'language': f"{language[exist['languages']]}"
            }