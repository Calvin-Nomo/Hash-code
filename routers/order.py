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

router = APIRouter(prefix="/order", tags=["order"])
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.get('/Order')
def get_order():
    sql_command="Select* from Orders" 
    cursor.execute(sql_command)
    order =cursor.fetchall()
    return order