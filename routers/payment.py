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

router = APIRouter( prefix="/payment", tags=["payment"])
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Payment')
def get_payment():
    sql_command="Select* from Payment" 
    cursor.execute(sql_command)
    payments=cursor.fetchall()
    return payments