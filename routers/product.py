from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)

cursor=DB.cursor()

router = APIRouter(prefix="/product", tags=["product"])

class Product(BaseModel):
    Product_Name:str
    Product_Description:str
    Category:str
    Unit_Price:float
    Image_Path:str


@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}


@router.get('/Product')
def get_product():
    sql_command="Select* from Product"
    cursor.execute(sql_command)
    product=cursor.fetchall()
    return product

@router.post('/create_product')
def create_product(product:Product):
    try:
        sql_command="""INSERT INTO Product(Product_Name,Product_Description,Category,Unit_Price,Image_link)
        VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command,(product.Product_Name,product.Product_Description,product.Category,product.Unit_Price,product.Image_Path))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the Product data to your database'
    }
