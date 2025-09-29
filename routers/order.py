from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
import pymysql
from datetime import datetime

DB= pymysql.connect(
    host="localhost",
    user="root",
    password="Bineli2006",
    database="Order_System", 
   cursorclass=pymysql.cursors.DictCursor  # so results come as dicts instead of tuples
)
class Order(BaseModel):
    No_Reservation:int 
    Order_Date: datetime 
    Order_Type: str
    No_Table: int 
    Note:str
    

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
@router.post("/create order")
def create_order(order:Order):
    try:
        sql_command="""INSERT INTO Orders(No_Reservation,Order_Date,Order_Type,No_Table,Note)
        VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(sql_command,(order.No_Reservation,order.Order_Date,order.Order_Type,order.No_Table,order.Note))
        DB.commit()
    except Exception as e:
        raise HTTPException(status_code=404,detail=(e))
    return{
'Message':'You Have successfully added the Order data to your database'
    }
