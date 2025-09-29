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

router = APIRouter( prefix="/reservation", tags=["reservation"])
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
