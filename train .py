from fastapi import FastAPI, Form, File, UploadFile, Depends
from pydantic import BaseModel
import pymysql
import shutil
import os

app = FastAPI()

# -------------------------------
# Database Connection
# -------------------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "yourpassword"
DB_NAME = "yourdatabase"

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# -------------------------------
# Upload Directory
# -------------------------------
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -------------------------------
# Pydantic Model
# -------------------------------
class Product(BaseModel):
    No_Product: int
    Product_Name: str
    Unit_Price: float
    Category: str
    Product_Description: str | None = None

# -------------------------------
# Dependency: Convert Form → Pydantic
# -------------------------------
def product_as_form(
    No_Product: int = Form(...),
    Product_Name: str = Form(...),
    Unit_Price: float = Form(...),
    Category: str = Form(...),
    Product_Description: str | None = Form(None),
) -> Product:
    return Product(
        No_Product=No_Product,
        Product_Name=Product_Name,
        Unit_Price=Unit_Price,
        Category=Category,
        Product_Description=Product_Description,
    )

# -------------------------------
# CREATE
# -------------------------------
@app.post("/add_product/")
async def add_product(
    product: Product = Depends(product_as_form),
    Image: UploadFile = File(...)
):
    try:
        # Save image
        file_path = os.path.join(UPLOAD_DIR, Image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(Image.file, buffer)

        # Insert into DB
        connection = get_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO Product 
                (No_Product, Product_Name, Unit_Price, Category, Product_Description, Image_link)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                product.No_Product,
                product.Product_Name,
                product.Unit_Price,
                product.Category,
                product.Product_Description,
                file_path
            ))
            connection.commit()

        return {"message": "Product created successfully", "product": product.dict(), "Image_Path": file_path}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# READ (All products)
# -------------------------------
@app.get("/products/")
async def get_products():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product")
            results = cursor.fetchall()
        return {"products": results}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# UPDATE
# -------------------------------
@app.put("/update_product/{product_id}")
async def update_product(
    product_id: int,
    product: Product = Depends(product_as_form),
    Image: UploadFile | None = File(None)
):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE No_Product=%s", (product_id,))
            existing = cursor.fetchone()
            if not existing:
                return {"error": f"Product {product_id} not found"}

        # Handle image (new or old)
        if Image:
            file_path = os.path.join(UPLOAD_DIR, Image.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(Image.file, buffer)
        else:
            file_path = existing["Image_link"]

        # Update DB
        with connection.cursor() as cursor:
            sql = """
                UPDATE Product
                SET Product_Name=%s, Unit_Price=%s, Category=%s, Product_Description=%s, Image_link=%s
                WHERE No_Product=%s
            """
            cursor.execute(sql, (
                product.Product_Name,
                product.Unit_Price,
                product.Category,
                product.Product_Description,
                file_path,
                product_id
            ))
            connection.commit()

        return {"message": f"Product {product_id} updated", "updated_data": product.dict(), "Image_Path": file_path}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# DELETE
# -------------------------------
@app.delete("/delete_product/{product_id}")
async def delete_product(product_id: int):
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Product WHERE No_Product=%s", (product_id,))
            product = cursor.fetchone()
            if not product:
                return {"error": f"Product {product_id} not found"}

            cursor.execute("DELETE FROM Product WHERE No_Product=%s", (product_id,))
            connection.commit()

        # Remove image file
        if product["Image_link"] and os.path.exists(product["Image_link"]):
            os.remove(product["Image_link"])

        return {"message": f"Product {product_id} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
