from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- Allow your frontend access ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database connection ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="smartmenu"
)
cursor = db.cursor(dictionary=True)

# --- Pydantic model ---
class SystemSettings(BaseModel):
    language: str
    currency: str
    business_name: str
    business_address: str
    business_website: str
    receipt_footer: str
    show_qr: bool

# --- GET settings ---
@app.get("/settings", response_model=SystemSettings)
def get_settings():
    cursor.execute("SELECT * FROM system_settings ORDER BY id DESC LIMIT 1")
    settings = cursor.fetchone()
    if not settings:
        raise HTTPException(status_code=404, detail="No settings found")
    return settings

# --- UPDATE settings ---
@app.put("/settings")
def update_settings(settings: SystemSettings):
    cursor.execute("""
        UPDATE system_settings
        SET language=%s, currency=%s, business_name=%s,
            business_address=%s, business_website=%s,
            receipt_footer=%s, show_qr=%s
        WHERE id=1
    """, (
        settings.language, settings.currency, settings.business_name,
        settings.business_address, settings.business_website,
        settings.receipt_footer, settings.show_qr
    ))
    db.commit()
    return {"message": "Settings updated successfully"}
