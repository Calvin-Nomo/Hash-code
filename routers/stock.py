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

router = APIRouter(prefix="/stock", tags=["stock"])

class Stock(BaseModel):
    No_Product:int
    Quantity_Available:int
@router.get('/')
def greetings():
    return {
     "Message ":"Hello World" 
}
@router.post("/create_client")
def create_client(stock:Stock):
    try:
        sql_command="""INSERT INTO Stock(No_Product,Quantity_Available)
        VALUES(%s,%s)"""
        cursor.execute(sql_command,(stock.No_Product,stock.Quantity_Available))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the  Stock data to your database'
    }