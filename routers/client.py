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

router = APIRouter(
    prefix="/client", tags=["client"]
)

@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}

@router.get('/Client')
def get_client():
    sql_command="Select * from Clients" 
    cursor.execute(sql_command)
    clients=cursor.fetchall()
    return clients