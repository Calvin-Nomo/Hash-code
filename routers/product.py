from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dependencies import get_current_active_user,require_role
import os, shutil
import pymysql

DB = pymysql.connect(
    host="localhost",
    user="root",
    passwd="Bineli26",
    database="Order_System",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
cursor = DB.cursor()

app = FastAPI()
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
    image: UploadFile = File(...),current_user: dict = Depends(require_role(["admin"]))
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Return full URL
    return {
        "message": "Product created successfully",
        "Image_Path": f" {db_image_path} Save in the database"
    }

# Update product
@router.put("/update_product/{No_Product}")
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
