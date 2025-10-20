from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter
import logging
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from backend.data.credentials import Mysql_password,Database_Name
from dependencies import get_current_user,require_role
import os, shutil
import pymysql



DB= pymysql.connect(
    host="localhost",
    user="root",
    password=Mysql_password,
    database=Database_Name, 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)
app = FastAPI()
# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,  # can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # all logs saved here
    filemode="a",  # append mode
)
logger = logging.getLogger(__name__)
# ---------------- Rate Limiter ----------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please wait a moment."},
    )

cursor = DB.cursor()


router = APIRouter(prefix="/product", tags=["product"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve static files at /uploads
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# BaseModel
class Product(BaseModel):
    Product_Name: str
    Product_Description: str
    Category: str
    Price: float
    Image_Path: str

# current_user: dict = Depends(require_role(["waiter",'admin']))
# Fetch products with full URL
@router.get("/Product")
@limiter.limit("5/minute")
def get_product():
    cursor.execute("SELECT * FROM Product")
    products = cursor.fetchall()
    return products

# Create product
@router.post("/create_product")
async def create_product(
    Product_Name: str = Form(...),
    Product_Description: str = Form(...),
    Category: str = Form(...),
    Price: float = Form(...),
    image: UploadFile = File(...)
):
    try:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_image_path = f"{UPLOAD_DIR}/{image.filename}"

        cursor.execute(
            "INSERT INTO Product(Product_Name, Product_Description, Category, Price, Image_link) VALUES (%s,%s,%s,%s,%s)",
            (Product_Name, Product_Description, Category, Price, db_image_path)
        )
        product_id=cursor.lastrowid
        cursor.execute("INSERT INTO STOCK(No_Product)VALUES(%s)",(product_id,))
        logger.info(f"Product created: ID={product_id}, Name={Product_Name}, by User={get_current_user['username']}")
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    # Return full URL
    return {
        "message": "Product created successfully",
        "Image_Path": f" {db_image_path} Save in the database"
    }

# Update product
@router.put("/update_product/{No_Product}")
@limiter.limit("5/minute")
async def update_product(
    No_Product: int,
    Product_Name: str = Form(...),
    Product_Description: str = Form(...),
    Category: str = Form(...),
    Price: float = Form(...),
    image: UploadFile = File(None),current_user: dict = Depends(require_role(["admin"]))):
    cursor.execute("SELECT * FROM Product WHERE No_Product=%s", (No_Product,))
    prod = cursor.fetchone()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        if image:
            file_path = os.path.join(UPLOAD_DIR, image.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            db_image_path = f"{UPLOAD_DIR}/{image.filename}"
        else:
            db_image_path = prod['Image_link']

        cursor.execute(
            "UPDATE Product SET Product_Name=%s, Product_Description=%s, Category=%s, Price=%s, Image_link=%s WHERE No_Product=%s",
            (Product_Name, Product_Description, Category,Price, db_image_path, No_Product)
        )

        # Return full URL
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Product updated successfully", "Image_Path": {db_image_path}}
@router.delete("/delete_product/{No_Product}")
@limiter.limit("5/minute")
def delete_product(No_Product: int,current_user: dict = Depends(require_role(['admin']))):
    try:
        cursor.execute("SELECT * FROM Product WHERE No_Product=%s", (No_Product,))
        prod = cursor.fetchone()
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found")

        cursor.execute("DELETE FROM Product WHERE No_Product=%s", (No_Product,))
        DB.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"Message": f"Product with ID {No_Product} has been successfully deleted."}

app.include_router(router)
