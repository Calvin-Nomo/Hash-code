from fastapi import APIRouter
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